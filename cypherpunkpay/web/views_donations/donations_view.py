import json

from pyramid.view import view_config

from cypherpunkpay.app import App
from cypherpunkpay.web.views.base_view import BaseView


class DonationsViews(BaseView):

    def __init__(self, request):
        self.request = request

    @view_config(route_name='get_donations', renderer='jinja2')
    def get_donations(self):
        wait_a_sec = self.request.params.get('wait_a_sec', None) == 'true' and not App().is_fully_initialized()
        errors = json.loads(self.request.params.get('errors', '{}'))
        self.request.override_renderer = f'web/html/donations/theme_{self.theme()}/index.jinja2'
        return {
            'title': f'Donate{self.donations_cause_text()}',
            'donations_cause': self.app_config().donations_cause(),
            'donations_fiat_currency': self.app_config().donations_fiat_currency(),
            'donations_fiat_amounts': self.app_config().donations_fiat_amounts(),
            'wait_a_sec': wait_a_sec,
            'errors': errors
        }

    def donations_cause_text(self):
        donations_cause = self.app_config().donations_cause()
        if donations_cause:
            return f' to {donations_cause}'
        return ''
