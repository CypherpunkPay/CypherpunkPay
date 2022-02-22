import pyramid.request
from pyramid.authentication import AuthTktCookieHelper
from pyramid.authorization import ACLHelper, Authenticated, Everyone


# This is copied from the official docs:
# https://docs.pylonsproject.org/projects/pyramid/en/latest/whatsnew-2.0.html#upgrading-auth-20
class AuthPolicy:

    def __init__(self, secret: bytes, **kwargs):
        self.helper = AuthTktCookieHelper(secret, **kwargs)

    def identity(self, request: pyramid.request.Request):
        # define our simple identity as None or a dict with userid and principals keys
        identity = self.helper.identify(request)
        if identity is None:
            return None
        userid = identity['userid']  # identical to the deprecated request.unauthenticated_userid

        # verify the userid, just like we did before with groupfinder
        principals = self.user_groups(userid, request)

        # assuming the userid is valid, return a map with userid and principals
        if principals is not None:
            return {
                'userid': userid,
                'principals': principals,
            }

    def authenticated_userid(self, request):
        # defer to the identity logic to determine if the user id logged in
        # and return None if they are not
        identity = request.identity
        if identity is not None:
            return identity['userid']

    def permits(self, request, context, permission):
        # use the identity to build a list of principals, and pass them
        # to the ACLHelper to determine allowed/denied
        identity = request.identity
        principals = {Everyone}
        if identity is not None:
            principals.add(Authenticated)
            principals.add(identity['userid'])
            principals.update(identity['principals'])
        return ACLHelper().permits(context, principals, permission)

    def remember(self, request, userid, **kw):
        return self.helper.remember(request, userid, **kw)

    def forget(self, request, **kw):
        return self.helper.forget(request, **kw)

    def user_groups(self, username: str, _: pyramid.request.Request):
        if username == 'admin':
            return ['group:admins']
        else:
            return []
