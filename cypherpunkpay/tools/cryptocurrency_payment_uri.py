import urllib.parse
from decimal import Decimal


class CryptocurrencyPaymentUri(object):

    class UnsupportedFor(Exception):
        pass

    @classmethod
    def get(cls, coin: str, address: str, amount: [Decimal, None] = None, label: [str, None] = None, message: [str, None] = None):
        coin = coin.casefold()

        if amount is not None and not isinstance(amount, Decimal):
            raise TypeError('To avoid confusion the `amount` must be Decimal')

        if coin == 'btc':
            return cls._get_btc(address, amount, label, message)

        if coin == 'xmr':
            return cls._get_xmr(address, amount, label, message)

        raise CryptocurrencyPaymentUri.UnsupportedFor(coin)

    @classmethod
    def _get_btc(cls, address, amount, label, message):
        # BIP21: https://github.com/bitcoin/bips/blob/master/bip-0021.mediawiki
        params = {}
        if amount is not None: params['amount'] = f'{amount:f}'
        if label is not None: params['label'] = label
        if message is not None: params['message'] = message
        if params:
            encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            return f"bitcoin:{address}?{encoded_params}"
        else:
            return f"bitcoin:{address}"

    @classmethod
    def _get_xmr(cls, address, amount, label, message):
        # Monero specific: https://github.com/monero-project/monero/wiki/URI-Formatting
        params = {}
        if amount is not None: params['tx_amount'] = amount
        if label is not None: params['recipient_name'] = label
        if message is not None: params['tx_description'] = message
        if params:
            encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            return f"monero:{address}?{encoded_params}"
        else:
            return f"monero:{address}"
