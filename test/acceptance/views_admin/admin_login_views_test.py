from test.acceptance.acceptance_test_case import CypherpunkpayAcceptanceTestCase


class AdminLoginViewsTest(CypherpunkpayAcceptanceTestCase):

    VALID_USERNAME = 'admin'
    VALID_PASSWORD = 'admin123'

    # Login

    def test_unauthenticated_redirects_to_login(self):
        self.assert_redirected_to_login(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/')
        self.assert_redirected_to_login(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/charges')

    def test_get_admin_login(self):
        res = self.webapp.get(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/login', status=200)
        self.assertInBody(res, 'Login')

    def test_post_admin_login__missing_username_and_password(self):
        res = self.webapp.post(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/login', status=200)
        self.assertInBody(res, 'Login')
        self.assertInBody(res, 'Invalid username or password')

    def test_post_admin_login__empty_username_and_password(self):
        res = self.webapp.post(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/login', [
                    ('username', ''),
                    ('password', '')
        ], status=200)
        self.assertInBody(res, 'Login')
        self.assertInBody(res, 'Invalid username or password')

    def test_post_admin_login__invalid_username(self):
        res = self.webapp.post(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/login', [
                    ('username', 'invalid'),
                    ('password', self.VALID_PASSWORD)
        ], status=200)
        self.assertInBody(res, 'Login')
        self.assertInBody(res, 'Invalid username or password')

    def test_post_admin_login__invalid_password(self):
        res = self.webapp.post(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/login', [
                    ('username', self.VALID_USERNAME),
                    ('password', 'invalid')
        ], status=200)
        self.assertInBody(res, 'Login')
        self.assertInBody(res, 'Invalid username or password')

    def test_post_admin_login__valid(self):
        res = self.webapp.post(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/login', [
                    ('username', self.VALID_USERNAME),
                    ('password', self.VALID_PASSWORD)
        ], status=302)
        self.assertEqual(f'http://localhost/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/', res.location)

    # Register

    def test_login_redirects_to_register_if_no_users(self):
        self.app.db().delete_all_users()
        res = self.webapp.get(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/login', status=302)
        self.assertMatch(f'http://localhost/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/register', res.location)

    def test_get_admin_register(self):
        self.app.db().delete_all_users()
        res = self.webapp.get(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/register', status=200)
        self.assertInBody(res, 'Register')

    def test_post_admin_register__empty_password(self):
        self.app.db().delete_all_users()
        res = self.webapp.post(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/register', [('password', '  ')], status=200)
        self.assertInBody(res, 'Register')
        self.assertInBody(res, 'Password cannot be empty')

    def test_post_admin_register__password_confirmation_mismatch(self):
        self.app.db().delete_all_users()
        res = self.webapp.post(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/register', [
            ('password', 'abc'),
            ('password_conf', 'bbb')
        ], status=200)
        self.assertInBody(res, 'Register')
        self.assertInBody(res, 'Password and password confirmation do not match')

    def test_post_admin_register__valid(self):
        self.app.db().delete_all_users()
        res = self.webapp.post(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/register', [
            ('password', 'Test1234'),
            ('password_conf', 'Test1234')
        ], status=302)
        self.assertMatch(f'http://localhost/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/login', res.location)
        self.assertEqual(self.app.db().get_users_count(), 1)

    def assert_redirected_to_login(self, url):
        res = self.webapp.get(url, status=302)
        self.assertMatch(f'http://localhost/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/login', res.location)
