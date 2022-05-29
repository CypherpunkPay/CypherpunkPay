# !!!
# Remarks:
#   * DO NOT import this file. Importing will make session fixtures ran multiple times, causing errors.
#   * DO NOT rename this file. File must be named conftest.py to be auto-imported by pytest to look for fixtures.
#   * DO NOT put helpers here. This file is only for pytest fixtures.
# !!!
#
# Docs: https://stackoverflow.com/questions/34466027/in-pytest-what-is-the-use-of-conftest-py-files
#

import pytest
import webtest

import pyramid
from pyramid import paster, testing

import cypherpunkpay
from cypherpunkpay.globals import *
from cypherpunkpay import ConfigParser, set_btc_testnet, DummyJobScheduler, ExamplePriceTickers
from cypherpunkpay.models.user import User


@pytest.fixture(scope='session')
def instantiate_app():
    from tests.acceptance.acceptance_test_case import CypherpunkpayAcceptanceTestCase as base_class

    # SETUP
    pyramid.paster.setup_logging(the_test_ini_path())
    set_btc_testnet()
    config = ConfigParser(env='test').from_user_conf_files()
    base_class.app = cypherpunkpay.app.App(config=config, job_scheduler=DummyJobScheduler(), price_tickers=ExamplePriceTickers())
    db = base_class.app.db()
    db.reset_for_tests()
    admin_password_hash = '000186a05a1cdd05b365685e908c6de033cf83a2e3cc53c8611fc0945a6b5116c8d9b8abd3ca4cca254e0e933629c8148a6dc70032a124d56df804f9431c1c0499dd0ada'  # PBKDF2.hash('admin123')
    user = User(username='admin', password_hash=admin_password_hash)
    db.insert(user)

    yield

    # TEARDOWN
    base_class.app.close()
    base_class.app = None


@pytest.fixture(scope='function')
def acceptance_per_function_wrapper():
    from tests.acceptance.acceptance_test_case import CypherpunkpayAcceptanceTestCase as base_class

    # SETUP
    # Read test.ini [app:main]
    settings = pyramid.paster.get_appsettings(the_test_ini_path(), name='main')
    # Setup Pyramid globals (registry etc)
    pyramid.testing.setUp(settings=settings)
    # WebTest is initialized with generic WSGI application
    wsgi_app = cypherpunkpay.main(global_config=None, **settings)
    base_class.webapp = webtest.TestApp(wsgi_app)
    # Database
    base_class.app.db().execute('BEGIN')

    yield

    # TEARDOWN
    base_class.app.db().execute('ROLLBACK')
    pyramid.testing.tearDown()


def the_test_ini_path():
    return f"{dir_of(__file__)}/../../cypherpunkpay/config/test.ini"
