from decimal import Decimal

from tests.unit.test_case import CypherpunkpayTestCase
from cypherpunkpay.tools.cryptocurrency_payment_uri import CryptocurrencyPaymentUri


class CryptocurrencyPaymentUriTest(CypherpunkpayTestCase):

    def test_get_btc(self):
        # Address
        uri = CryptocurrencyPaymentUri.get('btc', '175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W')
        assert uri == 'bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W'

        # Address, amount
        uri = CryptocurrencyPaymentUri.get('btc', 'mgwm4YLsnPaSPfnQ5kdm3URz7ejXKBGxbV', amount=Decimal('0.00208907'))
        assert uri == 'bitcoin:mgwm4YLsnPaSPfnQ5kdm3URz7ejXKBGxbV?amount=0.00208907'

        # Address, amount, label, message
        uri = CryptocurrencyPaymentUri.get('btc', '175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W', amount=Decimal('50'), label='Luke-Jr', message='Donation for project xyz')
        assert uri == 'bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?amount=50&label=Luke-Jr&message=Donation%20for%20project%20xyz'

    def test_get_xmr(self):
        # Address
        uri = CryptocurrencyPaymentUri.get(
            'xmr',
            '46BeWrHpwXmHDpDEUmZBWZfoQpdc6HaERCNmx1pEYL2rAcuwufPN9rXHHtyUA4QVy66qeFQkn6sfK8aHYjA3jk3o1Bv16em'
        )
        assert uri == 'monero:46BeWrHpwXmHDpDEUmZBWZfoQpdc6HaERCNmx1pEYL2rAcuwufPN9rXHHtyUA4QVy66qeFQkn6sfK8aHYjA3jk3o1Bv16em'

        # Address, amount
        uri = CryptocurrencyPaymentUri.get(
            'xmr',
            '46BeWrHpwXmHDpDEUmZBWZfoQpdc6HaERCNmx1pEYL2rAcuwufPN9rXHHtyUA4QVy66qeFQkn6sfK8aHYjA3jk3o1Bv16em',
            amount=Decimal('239.390146789012')
        )
        assert uri == 'monero:46BeWrHpwXmHDpDEUmZBWZfoQpdc6HaERCNmx1pEYL2rAcuwufPN9rXHHtyUA4QVy66qeFQkn6sfK8aHYjA3jk3o1Bv16em?tx_amount=239.390146789012'

        # Address, amount, label, message
        uri = CryptocurrencyPaymentUri.get(
            'xmr',
            '46BeWrHpwXmHDpDEUmZBWZfoQpdc6HaERCNmx1pEYL2rAcuwufPN9rXHHtyUA4QVy66qeFQkn6sfK8aHYjA3jk3o1Bv16em',
            amount=Decimal('239.390146789012'),
            label='Luke-Jr',
            message='Donation for project xyz'
        )
        assert uri == 'monero:46BeWrHpwXmHDpDEUmZBWZfoQpdc6HaERCNmx1pEYL2rAcuwufPN9rXHHtyUA4QVy66qeFQkn6sfK8aHYjA3jk3o1Bv16em?tx_amount=239.390146789012&recipient_name=Luke-Jr&tx_description=Donation%20for%20project%20xyz'
