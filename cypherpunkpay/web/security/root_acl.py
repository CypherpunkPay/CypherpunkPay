from pyramid.security import Allow, Deny, Everyone


class RootACL(object):
    __acl__ = [
        (Allow, 'group:admins', 'admin')
        ]

    def __init__(self, request):
        pass
