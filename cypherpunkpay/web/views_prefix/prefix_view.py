from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config


# This is for the not-prefixed top level root path:
# / redirecting to the prefixed root
@view_config(route_name='get_root_not_prefixed')
def get_root_not_prefixed(request):
    return HTTPFound(request.route_url('get_root'))
