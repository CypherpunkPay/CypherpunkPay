from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from cypherpunkpay import App


# This is for the prefixed root path:
# /cypherpunkpay/
@view_config(route_name='get_root')
def get_root(request):
    if App().config().donations_enabled():
        return HTTPFound(request.route_url('get_donations'))
    if App().config().dummystore_enabled():
        return HTTPFound(request.route_url('get_dummystore_root'))
    return HTTPNotFound()
