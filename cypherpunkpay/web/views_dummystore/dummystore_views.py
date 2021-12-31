import logging as log

from decimal import Decimal

from pyramid.httpexceptions import HTTPOk, HTTPForbidden, HTTPBadRequest, HTTPNotFound
from pyramid.view import (view_config)

from cypherpunkpay import App
from cypherpunkpay.db.dev_examples import DevExamples
from cypherpunkpay.web.views.base_view import BaseView


class DummystoreViews(BaseView):

    @view_config(route_name='get_dummystore_root', renderer='web/html/dummystore/index.jinja2')
    def get_dummystore_root(self):
        orders = DevExamples().create_dummy_store_orders(self.db())
        return { 'orders': orders }

    @view_config(route_name='get_dummystore_order', renderer='web/html/dummystore/order.jinja2')
    def get_dummystore_order(self):
        uid = self.request.matchdict['uid']
        order = App().db().get_order_by_uid(uid)
        if not order:
            raise HTTPNotFound()
        return {'order': order}

    # POST /cypherpunkpay/dummystore/cypherpunkpay_payment_completed
    @view_config(route_name='post_cypherpunkpay_payment_completed')
    def post_cypherpunkpay_payment_completed(self):
        log.info(f'Received notification from CypherpunkPay: {self.request.body}')

        # Authenticate CypherpunkPay
        authorization_header = self.request.headers.get('Authorization')
        if not authorization_header == f'Bearer {self.app_config().cypherpunkpay_to_merchant_auth_token()}':
            return HTTPForbidden()

        # Parse body as JSON
        import json
        try:
            cypherpunkpay = json.loads(self.request.body)
        except json.decoder.JSONDecodeError as e:
            log.error(e)
            return HTTPBadRequest()

        untrusted = cypherpunkpay.get('untrusted', {})

        # Read order from database
        untrusted_order_id = untrusted.get('merchant_order_id')
        order = App().db().get_order_by_uid(untrusted_order_id)

        # Validate order data were not tampered with
        # Return 200 OK regardless to acknowledge callback reception so it won't get repeated
        if order is None:
            log.warning(f'Invalid merchant_order_id={untrusted_order_id}')
            return HTTPOk()
        if Decimal(untrusted.get('total', 0)) != order.total:
            log.warning(f'Invalid order total={untrusted.get("total")}')
            return HTTPOk()
        if untrusted.get('currency', '').casefold() != order.currency.casefold():
            log.warning(f'Invalid order currency={untrusted.get("currency")}')
            return HTTPOk()

        # Mark order as paid and initiate shipping
        order.payment_completed(cypherpunkpay['cc_total'], cypherpunkpay['cc_currency'])
        order.ship()
        self.db().save(order)

        return HTTPOk()

    # POST /cypherpunkpay/dummystore/cypherpunkpay_payment_failed
    @view_config(route_name='post_cypherpunkpay_payment_failed')
    def post_cypherpunkpay_payment_failed(self):
        log.info(f'Received notification from CypherpunkPay: {self.request.body}')

        # Authenticate CypherpunkPay
        authorization_header = self.request.headers.get('Authorization')
        if not authorization_header == f'Bearer {self.app_config().cypherpunkpay_to_merchant_auth_token()}':
            return HTTPForbidden()

        # Parse body as JSON
        import json
        try:
            cypherpunkpay = json.loads(self.request.body)
        except json.decoder.JSONDecodeError as e:
            log.error(e)
            return HTTPBadRequest()

        untrusted = cypherpunkpay.get('untrusted', {})

        # Read order from database
        untrusted_order_id = untrusted.get('merchant_order_id')
        order = App().db().get_order_by_uid(untrusted_order_id)

        # Validate order data were not tampered with
        # Return 200 OK regardless to acknowledge callback reception so it won't get repeated
        if order is None:
            log.warning(f'Invalid merchant_order_id={untrusted_order_id}')
            return HTTPOk()
        if Decimal(untrusted.get('total', 0)) != order.total:
            log.warning(f'Invalid order total={untrusted.get("total")}')
            return HTTPOk()
        if untrusted.get('currency', '').casefold() != order.currency.casefold():
            log.warning(f'Invalid order currency={untrusted.get("currency")}')
            return HTTPOk()

        order.dont_ship()
        self.db().save(order)

        return HTTPOk()
