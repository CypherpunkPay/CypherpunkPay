import requests

from test.internet.cypherpunkpay.cypherpunkpay_network_test_case import CypherpunkpayNetworkTestCase
from test.unit.cypherpunkpay.app.example_config import ExampleConfig
from cypherpunkpay.net.http_client.tor_http_client import TorHttpClient
from cypherpunkpay.net.tor_client.base_tor_circuits import BaseTorCircuits
from cypherpunkpay.net.tor_client.official_tor_circuits import OfficialTorCircuits


class TorHttpClientTest(CypherpunkpayNetworkTestCase):

    class MockTorCircuits(OfficialTorCircuits):
        def mark_as_broken(self, label):
            if label == 'shared':
                self.mark_as_broken_was_called = True

    def test_headers_like_tor_browser(self):
        http_client = TorHttpClient(self.official_tor)
        self.assertTorBrowserRequestHeaders(http_client)

    def test_marks_circuit_as_broken_on_exception(self):
        NON_EXISTING_URL = 'https://randomnonexistingurl.domain'
        tor = self.MockTorCircuits(config=ExampleConfig())
        http_client = TorHttpClient(tor)
        try:
            http_client.get(url=NON_EXISTING_URL, privacy_context='shared')
            self.fail()
        except requests.exceptions.RequestException as e:
            self.assertTrue(tor.mark_as_broken_was_called)
        finally:
            tor.close()

    # This test case assumes HTTP server is running on localhost:9050.
    # Normally, when you develop CypherpunkPay, you will have Tor socks proxy running there,
    # The Tor socks proxy is kind enough to reply in HTTP as well,
    # so we (ab)use it for our testing purposes.
    def test_localhost(self):
        http_client = TorHttpClient(self.official_tor)
        response = http_client.get_accepting_linkability('http://127.0.0.1:9050/')
        # The 501 is expected here because we HTTP GET to Tor binary socks proxy
        self.assertEqual(501, response.status_code)

    def test_post(self):
        http_client = TorHttpClient(self.official_tor)
        example_auth = {'Authorization': 'Bearer testtoken1234'}
        example_body = "abcdef  \t\n0"
        response = http_client.post('https://httpbin.org/anything', BaseTorCircuits.SHARED_CIRCUIT_ID, headers=example_auth, body=example_body, set_tor_browser_headers=False)
        httpbin_result = response.json()
        self.assertEqual('Bearer testtoken1234', httpbin_result['headers']['Authorization'])
        self.assertEqual(example_body, httpbin_result['data'])

    def test_creates_new_circuit_for_each_domain(self):
        http_client = TorHttpClient(self.official_tor)
        domain1_ip = http_client.get_accepting_linkability('https://api.myip.com/').json()['ip']
        domain2_ip = http_client.get_accepting_linkability('https://api.ipify.org?format=json').json()['ip']
        self.assertNotEqual(domain1_ip, domain2_ip)
