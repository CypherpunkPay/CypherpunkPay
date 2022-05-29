import pytest

from cypherpunkpay.net.http_client.clear_http_client import ClearHttpClient
from cypherpunkpay.net.http_client.tor_http_client import TorHttpClient
from cypherpunkpay.net.tor_client.official_tor_circuits import OfficialTorCircuits
from tests.unit.config.example_config import ExampleConfig


@pytest.fixture(scope='session')
def http_clients():
    # SETUP
    from tests.network.network_test_case import CypherpunkpayNetworkTestCase
    base_class = CypherpunkpayNetworkTestCase
    base_class.official_tor = OfficialTorCircuits(config=ExampleConfig())
    base_class.official_tor.connect_and_verify()
    base_class.clear_http_client = ClearHttpClient()
    base_class.tor_http_client = TorHttpClient(base_class.official_tor)

    yield

    # TEARDOWN
    base_class.official_tor.close()
    base_class.official_tor = None         # prevent accidental usage
    base_class.tor_http_client = None      # prevent accidental usage
    base_class.clear_http_client.close()
    base_class.clear_http_client = None    # prevent accidental usage
