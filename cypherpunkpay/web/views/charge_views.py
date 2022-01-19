import json

from pyramid.response import Response
from pyramid.view import (view_config)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest

from cypherpunkpay.app import App
from cypherpunkpay.lightning_node_clients.lnd_client import LightningException
from cypherpunkpay.models.charge import Charge

from cypherpunkpay.prices.price_tickers import PriceTickers
from cypherpunkpay.usecases.cancel_charge_uc import CancelChargeUC
from cypherpunkpay.usecases.create_charge_uc import CreateChargeUC
from cypherpunkpay.usecases.invalid_params import InvalidParams
from cypherpunkpay.usecases.pick_cryptocurrency_for_charge_uc import PickCryptocurrencyForChargeUC
from cypherpunkpay.web.views.base_view import BaseView


class ChargeViews(BaseView):

    def __init__(self, request):
        self.request = request

    @view_config(route_name='post_charge')
    def post_charge(self):
        params = self.request.params
        total = params.get('total')
        currency = params.get('currency')
        merchant_order_id = params.get('merchant_order_id')
        beneficiary = params.get('beneficiary')
        what_for = params.get('what_for')
        try:
            charge = CreateChargeUC(total=total, currency=currency, merchant_order_id=merchant_order_id, beneficiary=beneficiary, what_for=what_for).exec()
            if charge.is_active():
                location = self.request.route_url('get_charge', uid=charge.uid, ux_type='auto')
                return HTTPFound(location=location)
            else:
                location = self.request.route_url('get_charge_pick_coin', uid=charge.uid)
                return HTTPFound(location=location)
        except PriceTickers.Missing as e:
            location = self.request.route_url('get_donations', _query={'wait_a_sec': 'true'})
            return HTTPFound(location=location)  # HTTPServiceUnavailable()
        except InvalidParams as e:
            location = self.request.route_url('get_donations', _query={'errors': json.dumps(e.errors)})
            return HTTPFound(location=location)  #return HTTPBadRequest(e.errors)

    @view_config(route_name='get_charge_pick_coin', renderer='jinja2', http_cache=0)
    def get_charge_pick_coin(self):
        wait_a_sec = self.request.params.get('wait_a_sec', None) == 'true'
        lightning_error = self.request.params.get('lightning_error', None) == 'true'
        uid = self.request.matchdict['uid']
        charge = App().db().get_charge_by_uid(uid)
        if not charge:
            raise HTTPNotFound()
        if not charge.is_draft():
            # User clicked [BACK] in the browser. The coin is already picked. User cannot change it at this stage. User needs to cancel instead.
            location = self.request.route_url('get_charge', uid=charge.uid, ux_type='auto')
            return HTTPFound(location=location)
        title = f"Charge {charge.created_at.date().isoformat()} | {charge.uid}"
        self.request.override_renderer = f'{self.htmls()}/charge_pick_coin.jinja2'
        return {
            'title': title,
            'charge': charge,
            'wait_a_sec': wait_a_sec,
            'lightning_error': lightning_error,
            'coins': self.app_config().configured_coins(),
            'btc_lightning_enabled': self.app_config().btc_lightning_enabled()
        }

    @view_config(route_name='post_charge_pick_coin')
    def post_charge_pick_coin(self):
        uid = self.request.matchdict['uid']
        cc_currency = self.request.params.getone('cc_currency')
        lightning = False
        if cc_currency == 'btc-lightning':
            cc_currency = 'btc'
            lightning = True
        charge = App().db().get_charge_by_uid(uid)
        if not charge:
            raise HTTPNotFound()
        try:
            PickCryptocurrencyForChargeUC(charge=charge, cc_currency=cc_currency, lightning=lightning).exec()
        except InvalidParams as e:
            return HTTPBadRequest()
        except PriceTickers.Missing as e:
            location = self.request.route_url('get_charge_pick_coin', uid=charge.uid, _query={'wait_a_sec': 'true'})
            return HTTPFound(location=location)  # HTTPServiceUnavailable()
        except LightningException as e:
            location = self.request.route_url('get_charge_pick_coin', uid=charge.uid, _query={'lightning_error': 'true'})
            return HTTPFound(location=location)

        location = self.request.route_url('get_charge', uid=charge.uid, ux_type='auto')
        return HTTPFound(location=location)

    @view_config(route_name='post_charge_cancel')
    def post_charge_cancel(self):
        uid = self.request.matchdict['uid']
        charge = App().db().get_charge_by_uid(uid)
        if not charge:
            raise HTTPNotFound()
        CancelChargeUC(charge=charge).exec()
        location = self.exit_url(charge)
        return HTTPFound(location=location)

    def per_status_renderer(self, type, charge: Charge):
        if charge.is_completed():
            return f"{self.htmls()}/charge_completed.jinja2"

        if charge.is_cancelled():
            return f"{self.htmls()}/charge_cancelled.jinja2"

        if charge.is_expired() and charge.is_unpaid():
            return f"{self.htmls()}/charge_expired_to_complete__unpaid.jinja2"
        if charge.is_expired() and not charge.is_unpaid():
            return f"{self.htmls()}/charge_expired_to_complete__paid.jinja2"
        if charge.is_soft_expired_to_pay():
            return f"{self.htmls()}/charge_expired_to_pay.jinja2"

        if charge.is_awaiting() and charge.pay_status in {'paid', 'confirmed'}:
            return f"{self.htmls()}/charge_{charge.pay_status}.jinja2"
        if charge.is_awaiting() and charge.pay_status in ['unpaid', 'underpaid']:
            return f"{self.htmls()}/charge_{type}_{charge.pay_status}.jinja2"

        raise Exception(f"Unsupported charge pay_status={charge.pay_status}, status={charge.status}")

    def per_status_refresh_seconds(self, type, charge: Charge) -> int:
        if charge.pay_status in ['paid', 'confirmed']:
            return 10
        if charge.pay_status in ['unpaid', 'underpaid']:
            if charge.is_soft_expired_to_pay():
                return 10
            if type == 'auto':
                return 1
            if type == 'manual':
                return 60
        if charge.has_non_final_status():
            return 60
        return 0

    @view_config(route_name='get_charge_root')
    def get_charge_root(self):
        raise HTTPFound(location=self.request.route_url('get_charge', uid=self.request.matchdict['uid'], ux_type='auto'))

    @view_config(route_name='get_charge', renderer='jinja2', http_cache=0)
    def get_charge(self):
        # UID
        uid = self.request.matchdict['uid']
        charge = App().db().get_charge_by_uid(uid)
        if not charge:
            raise HTTPNotFound()

        # UX type (auto or manual)
        ux_type = self.request.matchdict['ux_type']
        if ux_type not in ['auto', 'manual']:
            raise HTTPNotFound()

        title = f"Charge {self.formatted_amount(charge.cc_total, charge.cc_currency)} | {charge.created_at.date().isoformat()} | {charge.uid}"
        refresh_s = self.per_status_refresh_seconds(ux_type, charge)
        self.request.override_renderer = self.per_status_renderer(ux_type, charge)

        return {'title': title, 'charge': charge, 'refresh': refresh_s}

    @view_config(route_name='get_charge_state_hash', http_cache=0)
    def get_charge_state_hash(self):
        uid = self.request.matchdict['uid']
        charge = App().db().get_charge_by_uid(uid)
        if not charge:
            raise HTTPNotFound()
        return Response(body=charge.state_hash_for_ui(), content_type='text/plain')

    def htmls(self):
        return f"web/html/charge/theme_{self.theme()}"
