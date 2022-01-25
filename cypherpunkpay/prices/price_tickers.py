from statistics import median

from cypherpunkpay.common import *
from cypherpunkpay.net.http_client.tor_http_client import BaseHttpClient
from cypherpunkpay.prices.cmc_coin_price_source import CmcCoinPriceSource
from cypherpunkpay.prices.messari_coin_price_source import MessariCoinPriceSource
from cypherpunkpay.prices.coingecko_coin_price_source import CoingeckoCoinPriceSource


class PriceTickers(object):

    class Missing(Exception):
        pass

    class UnsupportedCurrency(Exception):
        pass

    _coin_usd_price: Dict[str, Decimal]
    _fiat_usd_price: Dict[str, Decimal]
    _http_client: BaseHttpClient
    _required_price_freshness_in_minutes: int = 20
    _updated_at: datetime.datetime = None

    def __init__(self, http_client, required_price_freshness_in_minutes: int = 20):
        self._http_client = http_client
        self._required_price_freshness_in_minutes = required_price_freshness_in_minutes
        self._coin_usd_price = {'btc': None, 'xmr': None}
        self._fiat_usd_price = {
            'usd': Decimal(1),
            'eur': None, 'gbp': None, 'chf': None, 'cny': None, 'jpy': None,
            'cad': None, 'aud': None, 'nzd': None, 'rub': None, 'inr': None, 'krw': None, 'brl': None, 'mxn': None, 'pln': None, 'czk': None, 'zar': None
        }

    def price(self, coin: str, fiat: str) -> Decimal:
        if coin == fiat:
            return Decimal(1)

        coin = coin.casefold()
        if coin not in self._coin_usd_price.keys():
            raise PriceTickers.UnsupportedCurrency(coin)
        fiat = fiat.casefold()
        if fiat not in self._fiat_usd_price.keys():
            raise PriceTickers.UnsupportedCurrency(fiat)

        coin_price = self._coin_usd_price[coin]
        if coin_price is None:
            raise PriceTickers.Missing(coin)
        fiat_price = self._fiat_usd_price[fiat]
        if fiat_price is None:
            raise PriceTickers.Missing(fiat)
        if not self.is_up_to_date():
            if self._updated_at:
                log.error(f"PriceTickers are out of date. We can't create new charges. Active charges will be processed.")
            raise PriceTickers.Missing()

        return coin_price * fiat_price

    def usd_price(self, coin: str) -> Decimal:
        return self.price(coin, 'usd')

    def update(self):
        for coin in self._coin_usd_price.keys():
            self.update_coin(coin)
        self.update_fiats()
        self._updated_at = utc_now()

    def update_coin(self, coin):
        coin_prices = list(filter(None, [
            CmcCoinPriceSource(self._http_client).get(coin, 'usd'),
            CoingeckoCoinPriceSource(self._http_client).get(coin, 'usd'),
            MessariCoinPriceSource(self._http_client).get(coin, 'usd')
        ]))
        if len(coin_prices) > 0:
            median_coin_price = median(coin_prices)
            self._coin_usd_price[coin] = median_coin_price

    def update_fiats(self):
        res = self._http_client.get_accepting_linkability('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml')
        xml: str = res.text
        fiat_eur_price = {}
        for fiat in self._fiat_usd_price.keys():
            if fiat == 'eur':
                continue
            looking_for = f"'{fiat.upper()}'"
            price_start_ix = xml.index(looking_for) + 12
            price_end_ix = xml.index("'", price_start_ix)
            price_s = xml[price_start_ix:price_end_ix]
            price = Decimal(price_s)
            fiat_eur_price[fiat] = price

        usd_eur_price = fiat_eur_price['usd']
        self._fiat_usd_price['eur'] = Decimal(1) / usd_eur_price

        for fiat in fiat_eur_price.keys():
            self._fiat_usd_price[fiat] = fiat_eur_price[fiat] / usd_eur_price

        # https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml
        # https://www.dailyfx.com/forex-rates#currencies
        # https://www.fxstreet.com/rates-charts/rates
        # https://www.forexlive.com/LiveQuotes
        # https://www.easymarkets.com/eu/live-currency-rates/
        # https://www.smartcurrencyexchange.com/live-exchange-rates/
        # https://www.investing.com/currencies/live-currency-cross-rates
        # https://finance.yahoo.com/currencies

    def is_fully_initialized(self):
        try:
            self.price('btc', 'usd')
            self.price('xmr', 'czk')
        except self.Missing:
            return False
        return True

    def is_up_to_date(self):
        if self._updated_at is None:
            return False
        return self._updated_at > utc_ago(minutes=self._required_price_freshness_in_minutes)


class ExamplePriceTickers(PriceTickers):

    def __init__(self):
        super().__init__(None)
        self._coin_usd_price = {'btc': Decimal(10_000), 'xmr': Decimal(90)}
        self._fiat_usd_price = {'usd': Decimal('1'), 'eur': Decimal('0.9162'), 'gbp': Decimal('0.7701'), 'chf': Decimal('0.9753'), 'cny': Decimal('6.9702'), 'jpy': Decimal('109.9780'), 'cad': Decimal('1.3256'), 'aud': Decimal('1.4820'), 'nzd': Decimal('1.5422'), 'rub': Decimal('62.9952'), 'inr': Decimal('71.3161'), 'krw': Decimal('1180.1356'), 'brl': Decimal('4.3326'), 'mxn': Decimal('18.6250'), 'pln': Decimal('3.8990'), 'czk': Decimal('22.7945'), 'zar': Decimal('14.7760')}
        self._updated_at = utc_now()
