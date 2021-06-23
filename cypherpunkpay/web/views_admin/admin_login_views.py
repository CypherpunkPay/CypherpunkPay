from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.view import (view_config, forbidden_view_config)
from pyramid.security import (remember, forget)

from cypherpunkpay import App
from cypherpunkpay.common import *
from cypherpunkpay.models.user import User
from cypherpunkpay.tools.pbkdf2 import PBKDF2
from cypherpunkpay.web.views_admin.admin_base_view import AdminBaseView


class AdminLoginViews(AdminBaseView):

    @forbidden_view_config()
    def unauthenticated(self):
        location = self.request.route_url('admin_login')
        return HTTPFound(location=location)

    @view_config(route_name='admin_login', renderer='web/html/admin/login.jinja2')
    def admin_login(self):
        request: Request = self.request

        if self.db().get_users_count() == 0:
            return HTTPFound(location=request.route_url('admin_register'))

        title = 'Admin Login'
        message = ''
        username = ''
        if request.method == 'POST':
            username = request.params.get('username')
            password = request.params.get('password')
            user = App().db().get_user_by_username(username)
            if user and user.password_hash and PBKDF2.password_is_correct(password, user.password_hash):
                headers = remember(request, username)
                return HTTPFound(location=request.route_url('get_admin_root'), headers=headers)
            message = 'Invalid username or password'

        return dict(
            title=title,
            message=message,
            username=username,
            password='',
        )

    @view_config(route_name='admin_logout')
    def admin_logout(self):
        request = self.request
        headers = forget(request)
        url = request.route_url('admin_login')
        return HTTPFound(location=url, headers=headers)

    @view_config(route_name='admin_register', renderer='web/html/admin/register.jinja2')
    def admin_register(self):
        request: Request = self.request

        if self.db().get_users_count() > 0:
            return HTTPFound(location=request.route_url('admin_login'))

        message = ''
        if request.method == 'POST':
            username = 'admin'
            password = request.params.get('password')
            password_conf = request.params.get('password_conf')
            if is_blank(password):
                message = 'Password cannot be empty'
            elif password != password_conf:
                message = 'Password and password confirmation do not match'
            else:
                # Success
                user = User(
                    username=username,
                    password_hash=PBKDF2.hash(password)
                )
                self.db().insert(user)
                return HTTPFound(location=request.route_url('admin_login'))

        return dict(title='Admin Registration', message=message)
