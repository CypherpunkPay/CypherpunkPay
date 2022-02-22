# !!!
# Remarks:
#   * DO NOT import this file. Importing will make session fixtures ran multiple times, causing errors.
#   * DO NOT rename this file. File must be named conftest.py to be auto-imported by pytest to look for fixtures.
#   * DO NOT put helpers here. This file is only for pytest fixtures.
# !!!

import pytest
import webtest

import pyramid
from pyramid import paster, testing

import cypherpunkpay
from cypherpunkpay import ConfigParser, set_btc_testnet, DummyJobScheduler, ExamplePriceTickers

from test.acceptance.acceptance_test_case import CypherpunkpayAcceptanceTestCase


# This is once globally
@pytest.fixture(scope='session', autouse=True)
def acceptance_per_session_wrapper():
    acceptance_per_session_setup()
    yield
    acceptance_per_session_teardown()


def acceptance_per_session_setup():
    # Logging
    pyramid.paster.setup_logging(the_test_ini_path())

    # Config
    config = ConfigParser(env='test').from_user_conf_files()
    set_btc_testnet()

    # Application
    CypherpunkpayAcceptanceTestCase.app = cypherpunkpay.app.App(config=config, job_scheduler=DummyJobScheduler(), price_tickers=ExamplePriceTickers())

    # Database
    CypherpunkpayAcceptanceTestCase.app.db().reset_for_tests()


def acceptance_per_session_teardown():
    CypherpunkpayAcceptanceTestCase.app.close()
    CypherpunkpayAcceptanceTestCase.app = None


# This is once per each test method
@pytest.fixture(scope='function', autouse=True)
def acceptance_per_function_wrapper():
    acceptance_per_function_setup()
    yield
    acceptance_per_function_teardown()


def acceptance_per_function_setup():
    # Read test.ini [app:main]
    settings = pyramid.paster.get_appsettings(the_test_ini_path(), name='main')
    # Setup Pyramid globals (registry etc)
    pyramid.testing.setUp(settings=settings)
    # WebTest is initialized with generic WSGI application
    CypherpunkpayAcceptanceTestCase.webapp = webtest.TestApp(cypherpunkpay.main(global_config=None, **settings))
    # Database
    CypherpunkpayAcceptanceTestCase.app.db().reset_for_tests()
    # Admin user
    from cypherpunkpay.models.user import User
    from cypherpunkpay.tools.pbkdf2 import PBKDF2
    user = User(username='admin', password_hash=PBKDF2.hash('admin123'))
    CypherpunkpayAcceptanceTestCase.app.db().insert(user)


def acceptance_per_function_teardown():
    pyramid.testing.tearDown()


def the_test_ini_path():
    from test.unit.test_case import CypherpunkpayTestCase
    return f"{CypherpunkpayTestCase.script_dir(__file__)}/../../cypherpunkpay/config/test.ini"
