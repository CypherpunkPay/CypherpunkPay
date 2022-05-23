from typing import Optional

from cypherpunkpay.net.http_client.clear_http_client import ClearHttpClient
from cypherpunkpay.net.tor_client.base_tor_circuits import BaseTorCircuits
from tests.unit.config.example_config import ExampleConfig
from tests.unit.test_case import CypherpunkpayTestCase
from cypherpunkpay.net.http_client.tor_http_client import TorHttpClient
from cypherpunkpay.net.tor_client.official_tor_circuits import OfficialTorCircuits


class CypherpunkpayNetworkTestCase(CypherpunkpayTestCase):

    official_tor: Optional[OfficialTorCircuits] = None
    clear_http_client: Optional[ClearHttpClient] = None

    XMR_STAGENET_REMOTE_HOST = 'stagenet.community.rino.io'
    XMR_STAGENET_REMOTE_PORT = 38081

    @classmethod
    def setup_class(cls):
        cls.official_tor = OfficialTorCircuits(config=ExampleConfig())
        cls.official_tor.connect_and_verify()
        cls.tor_http_client = TorHttpClient(cls.official_tor)
        cls.clear_http_client = ClearHttpClient()

    @classmethod
    def teardown_class(cls):
        cls.official_tor.close()
        cls.official_tor = None
        cls.clear_http_client.close()
        cls.clear_http_client = None

    def assertTorBrowserRequestHeaders(self, http_client):
        res = http_client.get(url='https://httpbin.org/headers', privacy_context='shared')
        headers = res.json()['headers']
        self.assertEqual(headers['User-Agent'], 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0')
        self.assertEqual(headers['Accept-Encoding'], 'gzip, deflate')
        self.assertEqual(headers['Accept-Language'], 'en-US,en;q=0.5')
        self.assertEqual(headers['Upgrade-Insecure-Requests'], '1')
        self.assertEqual(headers['Accept'], 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
