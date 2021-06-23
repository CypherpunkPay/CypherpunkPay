from test.internet.cypherpunkpay.cypherpunkpay_network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.prices.price_tickers import PriceTickers


class PriceTickersTest(CypherpunkpayNetworkTestCase):

    def test_prices(self):
        pt = PriceTickers(self.tor_http_client)

        pt.update()

        # USD

        btc_usd_price = pt.price(coin='btc', fiat='usd')
        self.assertTrue(1_000 < btc_usd_price < 100_000)

        xmr_usd_price = pt.price(coin='xmr', fiat='usd')
        self.assertTrue(10 < xmr_usd_price < 1000)

        # EUR

        btc_eur_price = pt.price(coin='btc', fiat='eur')
        self.assertTrue(btc_eur_price < btc_usd_price)

        xmr_eur_price = pt.price(coin='xmr', fiat='eur')
        self.assertTrue(xmr_eur_price < xmr_usd_price)
