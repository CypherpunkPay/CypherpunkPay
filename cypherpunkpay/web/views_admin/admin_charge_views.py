from pyramid.view import (view_config)

from cypherpunkpay import App
from cypherpunkpay.usecases.report_charges_uc import ReportChargesUC
from cypherpunkpay.web.views_admin.admin_base_view import AdminBaseView


class AdminChargeViews(AdminBaseView):

    @view_config(route_name='get_admin_charges', permission='admin', renderer='web/html/admin/charges.jinja2')
    def get_admin_charges(self):
        charges = App().db().get_recently_created_charges()
        cr_7d, cr_all_time = ReportChargesUC(self.db()).exec()
        return {
            'title': 'Admin Charges',
            'charges': charges,
            'cr': cr_all_time
        }
