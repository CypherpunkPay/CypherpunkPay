from typing import Optional

import pytest

from cypherpunkpay.net.http_client.clear_http_client import ClearHttpClient
from cypherpunkpay.net.tor_client.official_tor_circuits import OfficialTorCircuits

from tests.unit.test_case import CypherpunkpayTestCase


@pytest.mark.usefixtures('http_clients')
class CypherpunkpayNetworkTestCase(CypherpunkpayTestCase):

    official_tor: Optional[OfficialTorCircuits] = None
    clear_http_client: Optional[ClearHttpClient] = None

    XMR_STAGENET_REMOTE_HOST = 'stagenet.community.rino.io'
    XMR_STAGENET_REMOTE_PORT = 38081

    def assertTorBrowserRequestHeaders(self, http_client):
        res = http_client.get(url='https://httpbin.org/headers', privacy_context='shared')
        headers = res.json()['headers']
        self.assertEqual(headers['User-Agent'], 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0')
        self.assertEqual(headers['Accept-Encoding'], 'gzip, deflate')
        self.assertEqual(headers['Accept-Language'], 'en-US,en;q=0.5')
        self.assertEqual(headers['Upgrade-Insecure-Requests'], '1')
        self.assertEqual(headers['Accept'], 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
