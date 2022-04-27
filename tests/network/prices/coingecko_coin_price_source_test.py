from decimal import Decimal

from tests.network.network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.prices.coingecko_coin_price_source import CoingeckoCoinPriceSource


class CoingeckoCoinPriceSourceTest(CypherpunkpayNetworkTestCase):

    def test_get(self):
        source = CoingeckoCoinPriceSource(self.tor_http_client)

        price = source.get('btc', 'usd')
        self.assertTrue(isinstance(price, Decimal))
        self.assertTrue(1_000 < price < 100_000)

        price = source.get('xmr', 'usd')
        self.assertTrue(isinstance(price, Decimal))
        self.assertTrue(10 < price < 1000)
