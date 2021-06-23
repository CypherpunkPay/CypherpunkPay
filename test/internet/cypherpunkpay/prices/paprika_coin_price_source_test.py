from decimal import Decimal
from unittest import skip

from test.internet.cypherpunkpay.cypherpunkpay_network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.prices.paprika_coin_price_source import PaprikaCoinPriceSource


class PaprikaCoinPriceSourceTest(CypherpunkpayNetworkTestCase):

    @skip
    def test_get(self):
        source = PaprikaCoinPriceSource(self.tor_http_client)

        price = source.get('btc', 'usd')
        self.assertTrue(isinstance(price, Decimal))
        self.assertTrue(1_000 < price < 100_000)

        price = source.get('xmr', 'usd')
        self.assertTrue(isinstance(price, Decimal))
        self.assertTrue(10 < price < 1000)
