from pyramid.view import (view_config)

from cypherpunkpay.usecases.report_charges_uc import ReportChargesUC
from cypherpunkpay.web.views_admin.admin_base_view import AdminBaseView


class AdminStatsViews(AdminBaseView):

    @view_config(route_name='get_admin_stats', permission='admin', renderer='web/html/admin/stats.jinja2')
    def get_admin_stats(self):
        cr_7d, cr_all_time = ReportChargesUC(self.db()).exec()
        return {
            'title': 'Admin Stats',
            'cr_7d': cr_7d,
            'cr_all_time': cr_all_time
        }
