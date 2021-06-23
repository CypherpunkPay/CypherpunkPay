from pyramid.httpexceptions import HTTPFound
from pyramid.view import (view_config)

from cypherpunkpay.web.views_admin.admin_base_view import AdminBaseView


class AdminRootView(AdminBaseView):

    @view_config(route_name='get_admin_root', permission='admin')
    def get_admin_root(self):
        return HTTPFound(location=self.request.route_url('get_admin_charges'))
