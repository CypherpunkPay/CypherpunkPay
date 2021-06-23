from test.internet.cypherpunkpay.cypherpunkpay_network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.net.http_client.clear_http_client import ClearHttpClient
from cypherpunkpay.net.tor_client.base_tor_circuits import BaseTorCircuits


class ClearHttpClientTest(CypherpunkpayNetworkTestCase):

    def test_headers_like_tor_browser(self):
        with ClearHttpClient(self.official_tor) as http_client:
            self.assertTorBrowserRequestHeaders(http_client)

    def test_post(self):
        with ClearHttpClient(self.official_tor) as http_client:
            example_auth = {'Authorization': 'Bearer testtoken1234'}
            example_body = "abcdef  \t\n0"
            response = http_client.post('https://httpbin.org/anything', BaseTorCircuits.SHARED_CIRCUIT_ID, headers=example_auth, body=example_body, set_tor_browser_headers=False)
            httpbin_result = response.json()
            self.assertEqual('Bearer testtoken1234', httpbin_result['headers']['Authorization'])
            self.assertEqual(example_body, httpbin_result['data'])
