from decimal import Decimal

from test.network.network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.prices.cmc_coin_price_source import CmcCoinPriceSource


class CmcCoinPriceSourceTest(CypherpunkpayNetworkTestCase):

    def test_get(self):
        source = CmcCoinPriceSource(self.tor_http_client)

        price = source.get('btc', 'usd')
        self.assertTrue(isinstance(price, Decimal))
        self.assertTrue(1_000 < price < 100_000)

        price = source.get('xmr', 'usd')
        self.assertTrue(isinstance(price, Decimal))
        self.assertTrue(10 < price < 1000)
