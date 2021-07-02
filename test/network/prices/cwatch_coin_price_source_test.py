from decimal import Decimal

from test.network.network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.prices.cwatch_coin_price_source import CwatchCoinPriceSource


class CwatchCoinPriceSourceTest(CypherpunkpayNetworkTestCase):

    def test_get(self):
        source = CwatchCoinPriceSource(self.tor_http_client)

        price = source.get('btc', 'usd')
        self.assertTrue(isinstance(price, Decimal))
        self.assertTrue(1_000 < price < 100_000)

        price = source.get('xmr', 'usd')
        self.assertTrue(isinstance(price, Decimal))
        self.assertTrue(10 < price < 1000)
