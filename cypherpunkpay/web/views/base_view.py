from decimal import Decimal
from typing import List

from cypherpunkpay import Config, App
from cypherpunkpay.db.db import DB
from cypherpunkpay.models.charge import Charge


class BaseView(object):

    def __init__(self, request):
        self.request = request

    def background_coin_network_css_class(self, currency: str = None) -> str:
        if currency:
            currency = currency.casefold()
        else:
            currency = 'btc'
        if currency == 'btc' and self.app_config().btc_testnet():
            return 'testnet'
        if currency == 'xmr' and self.app_config().xmr_stagenet():
            return 'stagenet'
        return ''

    def html_formatted_currency_amount(self, value: Decimal, currency: str, select_amount=False):
        if self.is_fiat(currency):
            return self.formatted_currency_amount(value, currency)
        else:
            if currency == 'btc':
                amount = Decimal(value)  # / 10**8  # satoshi
                amount_s = f'{amount:.8f}'
                significant = amount_s[:-4]
                insignificant = amount_s[-4:]

            if currency == 'sats':
                amount = Decimal(value)  # / 10**8  # satoshi
                amount_s = f'{amount}'
                significant = amount_s[:-4]
                insignificant = amount_s[-4:]

            if currency == 'xmr':
                amount = Decimal(value)  # / 10**12  # piconero
                amount_s = f'{amount:.12f}'
                significant = amount_s[0:-10]
                insignificant = amount_s[-10:]

            amount_s = f'<span class="">{significant}</span><span class="has-text-lighter">{insignificant}</span>'

            if select_amount:
                amount_s = f'<span class="select-all">{amount_s}</span>'

            return f'{amount_s}&nbsp;{self.coin_symbol(currency)}'

    def formatted_currency_amount(self, value: Decimal, currency: str, select_amount=False):
        if self.is_fiat(currency):
            currency = currency.upper()
            amount = Decimal(value)
            amount_s = f'{amount:.2f}'
            if amount_s.endswith('.00'):
                amount_s = amount_s[0:-3]
            if currency in ['USD', 'CAD', 'AUD', 'NZD']:
                return f'${amount_s}'
            if currency == 'EUR':
                return f'{amount_s}\xa0€'
            if currency == 'CNY':
                return f'¥{amount_s}'
            if currency == 'GBP':
                return f'£{amount_s}'
            if currency == 'CHF':
                return f'CHF\xa0{amount_s}'
            if currency == 'JPY':
                return f'￥{amount_s}'
            if currency == 'RUB':
                return f'{amount_s}\xa0₽'
            if currency == 'BRL':
                return f'R$\xa0{amount_s}'
            if currency == 'KRW':
                return f'₩{amount_s}'
            if currency == 'CZK':
                return f'{amount_s}\xa0Kč'
            if currency == 'PLN':
                return f'{amount_s}\xa0zł'
            if currency == 'ZAR':
                return f'R{amount_s}'

            return f'{amount_s}\xa0{currency}'
        else:
            return self.formatted_amount(value, currency, select_amount)

    def formatted_amount(self, value: Decimal, currency: str, select_amount=False):
        currency = currency.casefold()
        amount_s = None
        currency_s = None

        if currency == 'btc':
            amount = Decimal(value) #/ 10**8  # satoshi
            amount_s = f'{amount:.8f}'
            amount_s = self.rstrip_amount(amount_s)
            currency_s = self.coin_symbol(currency)

        if currency == 'sats':
            amount = Decimal(value) #/ 10**8  # satoshi
            amount_s = f'{amount}'
            amount_s = self.rstrip_amount(amount_s)
            currency_s = self.coin_symbol(currency)

        if currency == 'xmr':
            amount = Decimal(value) #/ 10**12  # piconero
            amount_s = f'{amount:.12f}'.rstrip('0')
            amount_s = self.rstrip_amount(amount_s)
            currency_s = self.coin_symbol(currency)

        if self.is_fiat(currency):
            amount = Decimal(value) #/ 100  # cents
            amount_s = f'{amount:.2f}'
            if amount_s.endswith('.00'):
                amount_s = amount_s[0:-3]
            currency_s = currency.upper()

        if select_amount:
            amount_s = f'<span class="select-all">{amount_s}</span>'

        return f'{amount_s} {currency_s}'

    def rstrip_amount(self, amount_s):
        if '.' in amount_s:
            amount_s = amount_s.rstrip('0')
        if amount_s.endswith('.'):
            amount_s = amount_s.rstrip('.')
        return amount_s

    def fiat_locales(self):
        return {
            'usd': 'en_US',

            'eur': 'de_DE',
            'gbp': 'en_GB',
            'cny': 'zh_CN',
            'chf': 'de_CH',
            'jpy': 'ja_JP',

            'cad': 'en_CA',
            'aud': 'en_AU',
            'nzd': 'en_NZ',
            'rub': 'ru_RU',
            'inr': 'hi_IN',
            'krw': 'ko_KR',
            'brl': 'pt_BR',
            'mxn': 'es_MX',
            'pln': 'pl_PL',
            'czk': 'cs_CZ',
            'zar': 'af_ZA'
        }

    def coin_denominations(self) -> List[str]:
        coins = self.app_config().configured_coins()
        if 'btc' in coins:
            # Special treatment to have both sats and BTC
            coins = ['sats'] + coins
        return coins

    def supported_fiats(self):
        return Config.supported_fiats()

    def top_supported_fiats(self):
        return self.supported_fiats()[:4]

    def bottom_supported_fiats(self):
        return self.supported_fiats()[4:]

    def fiat_locale(self, currency):
        return self.fiat_locales()[currency.casefold()]

    def is_fiat(self, currency):
        return currency.casefold() in self.fiat_locales().keys()

    def coin_symbol(self, currency: str):
        return 'sats' if currency == 'sats' else currency.upper()

    def formatted_merchant_action(self, charge: Charge):
        if charge.is_draft():
            return '<span class="has-text-grey-light">nothing <br />(waiting for user to pick cryptocurrency)</span>'
        if charge.is_awaiting():
            if charge.is_unpaid():
                return '<span class="has-text-grey-light">nothing <br />(waiting for user to pay)</span>'
            elif charge.is_underpaid():
                return '<span class="has-text-grey-light">nothing <br />(waiting for user to pay remaining amount)</span>'
            elif charge.is_paid():
                return '<span class="has-text-grey-light">nothing <br />(waiting for network confirmations)</span>'
            else:
                return '<span class="has-text-grey-light">nothing <br />(waiting for more network confirmations)</span>'
        if charge.is_expired():
            if charge.is_unpaid():
                return '<span class="has-text-grey-light">nothing</span>'
            if charge.is_underpaid():
                return f'<span class="has-text-danger-dark">user paid less than requested; wait for enough network confirmations and then refund</span>'
            else:
                return f'<span class="has-text-danger-dark">payment failed to fully confirm before charge expiry; wait for enough network confirmations and then manually complete or refund</span>'
        if charge.is_cancelled():
            if charge.is_unpaid():
                return '<span class="has-text-grey-light">nothing</span>'
            else:
                return f'<span class="has-text-danger-dark">wait for enough network confirmations and then manually refund</span>'
        if charge.is_completed():
            return '<span class="tag is-success">ship</span>'

    # This returns exit-from-CypherpunkPay URL. Depending on the context this is used for:
    # [Cancel Payment]
    # [Back]
    # [Back to Merchant]
    # [Back to Donations]
    def exit_url(self, charge: Charge):
        if charge.is_donation():
            return self.request.route_url('get_donations')
        else:
            merchant_url = self.app_config().back_to_merchant_url()
            if merchant_url:
                merchant_order_url = merchant_url.replace('{merchant_order_id}', charge.merchant_order_id or '')
                return merchant_order_url
            return None

    def app(self) -> App:
        # This is only to force type hints on App()
        return App()

    def db(self) -> DB:
        # This is only to force type hints on App()
        return self.app().db()

    def app_config(self) -> Config:
        return self.app().config()

    def theme(self) -> str:
        return self.app_config().theme()

    def block_explorer_url(self, charge: Charge):
        if charge.cc_currency == 'btc' and not charge.is_lightning():
            if self.app().config().btc_mainnet():
                return f'https://blockstream.info/address/{charge.cc_address}'
            else:
                return f'https://blockstream.info/testnet/address/{charge.cc_address}'
