from tests.unit.test_case import CypherpunkpayTestCase, Decimal

from cypherpunkpay.web.base_view import BaseView


class BaseViewTest(CypherpunkpayTestCase):

    def test_formatted_currency_amount(self):
        self.assertCurrencyFormat('1099.4 ', 'usd', '$1099.40')
        self.assertCurrencyFormat('1099.4 ', 'eur', '1099.40\xa0€')
        self.assertCurrencyFormat('1099.4 ', 'cny', '¥1099.40')
        self.assertCurrencyFormat('1099.4 ', 'gbp', '£1099.40')
        self.assertCurrencyFormat('1099.4 ', 'chf', 'CHF\xa01099.40')
        self.assertCurrencyFormat('1099.4 ', 'jpy', '￥1099.40')
        self.assertCurrencyFormat('1099.4 ', 'cad', '$1099.40')
        self.assertCurrencyFormat('1099.4 ', 'aud', '$1099.40')
        self.assertCurrencyFormat('1099.4 ', 'nzd', '$1099.40')
        self.assertCurrencyFormat('1099.4 ', 'brl', 'R$\xa01099.40')
        self.assertCurrencyFormat('1099.4 ', 'krw', '₩1099.40')
        self.assertCurrencyFormat('1099.4 ', 'czk', '1099.40\xa0Kč')
        self.assertCurrencyFormat('1099.4 ', 'pln', '1099.40\xa0zł')
        self.assertCurrencyFormat('1099.4 ', 'zar', 'R1099.40')

        # self.assertCurrencyFormat('1099.4 ', 'usd', '$1,099.40')
        # self.assertCurrencyFormat('1099.4 ', 'eur', '1.099,40\xa0€')
        # self.assertCurrencyFormat('1099.4 ', 'cny', '¥1,099.40')
        # self.assertCurrencyFormat('1099.4 ', 'gbp', '£1,099.40')
        # self.assertCurrencyFormat('1099.4 ', 'chf', 'CHF\xa01’099.40')
        # self.assertCurrencyFormat('1099.4 ', 'jpy', '￥1,099')
        # self.assertCurrencyFormat('1099.4 ', 'cad', '$1,099.40')
        # self.assertCurrencyFormat('1099.4 ', 'aud', '$1,099.40')
        # self.assertCurrencyFormat('1099.4 ', 'nzd', '$1,099.40')
        # self.assertCurrencyFormat('1099.4 ', 'brl', 'R$\xa01.099,40')
        # self.assertCurrencyFormat('1099.4 ', 'krw', '₩1,099')
        # self.assertCurrencyFormat('1099.4 ', 'czk', '1\xa0099,40\xa0Kč')
        # self.assertCurrencyFormat('1099.4 ', 'pln', '1\xa0099,40\xa0zł')
        # self.assertCurrencyFormat('1099.4 ', 'zar', 'R1\xa0099,40')

    def test_formatted_amount(self):
        self.assertFormat('1', 'btc', '1 BTC')
        self.assertFormat('1.1', 'btc', '1.1 BTC')
        self.assertFormat('0.00000001', 'btc', '0.00000001 BTC')
        self.assertFormat('3.12300000', 'btc', '3.123 BTC')
        self.assertFormat('21000', 'btc', '21000 BTC')
        self.assertFormat('13_500_999.12345678', 'btc', '13500999.12345678 BTC')

        self.assertFormat('1', 'xmr', '1 XMR')
        self.assertFormat('0.000000000001', 'xmr', '0.000000000001 XMR')
        self.assertFormat('3.12300000', 'xmr', '3.123 XMR')
        self.assertFormat('13_500_999.123456789012', 'xmr', '13500999.123456789012 XMR')

        self.assertFormat('1', 'usd', '1 USD')
        self.assertFormat('1.1', 'usd', '1.10 USD')
        self.assertFormat('1.11', 'usd', '1.11 USD')
        self.assertFormat('13_500_999.99', 'usd', '13500999.99 USD')

    def assertFormat(self, amount_decimal, currency, expected):
        return self.assertEqual(expected, BaseView(None).formatted_amount(Decimal(amount_decimal), currency))

    def assertCurrencyFormat(self, amount_decimal, currency, expected):
        return self.assertEqual(expected, BaseView(None).formatted_currency_amount(Decimal(amount_decimal), currency))
