import pyramid
from pyramid import paster, testing
import webtest

import cypherpunkpay
from cypherpunkpay.common import *
from cypherpunkpay import ConfigParser, set_btc_testnet, DummyJobScheduler, ExamplePriceTickers
from cypherpunkpay.app import App
from cypherpunkpay.models.user import User
from cypherpunkpay.tools.pbkdf2 import PBKDF2

from test.unit.cypherpunkpay.cypherpunkpay_test_case import CypherpunkpayTestCase


class CypherpunkpayAppTestCase(CypherpunkpayTestCase):

    @classmethod
    def setUpClass(cls):
        # Logging
        remove_file_if_present(cls.the_test_log_path())
        pyramid.paster.setup_logging(cls.the_test_ini_path())

        # Application
        config = ConfigParser(env='test').from_user_conf_files()
        set_btc_testnet()
        App(config=config, job_scheduler=DummyJobScheduler(), price_tickers=ExamplePriceTickers())

    @classmethod
    def tearDownClass(cls):
        # this gets called multiple times, very weird
        # App().close()
        pass

    def setUp(self):
        # Read test.ini [app:main]
        settings = pyramid.paster.get_appsettings(self.the_test_ini_path(), name='main')
        # Setup Pyramid globals (registry etc)
        pyramid.testing.setUp(settings=settings)
        # WebTest is initialized with generic WSGI application
        self.webapp = webtest.TestApp(cypherpunkpay.main(global_config=None, **settings))
        # Database
        App().db().reset_for_tests()
        # Admin user
        user = User(username='admin', password_hash=PBKDF2.hash('admin123'))
        App().db().insert(user)

    def tearDown(self):
        pyramid.testing.tearDown()

    @staticmethod
    def the_test_ini_path():
        return f"{CypherpunkpayTestCase.script_dir(__file__)}/../../../cypherpunkpay/config/test.ini"

    @staticmethod
    def the_test_log_path():
        return f"{CypherpunkpayTestCase.script_dir(__file__)}/../../../log/test.log"

    def assertInBody(self, response, expected_content: str):
        self.assertIn(expected_content, response.body.decode('utf-8'))

    def assertNotInBody(self, response, expected_content: str):
        self.assertNotIn(expected_content, response.body.decode('utf-8'))

    def admin_prefix(self):
        return App().get_admin_unique_path_segment()

    def login(self):
        self.webapp.post(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/login', [
            ('username', 'admin'),
            ('password', 'admin123')
        ], status=302)   # make sure login successful
