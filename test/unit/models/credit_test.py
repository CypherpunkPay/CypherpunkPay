from cypherpunkpay.models.credit import Credit
from test.unit.test_case import CypherpunkpayTestCase


class CreditTest(CypherpunkpayTestCase):

    def test_is_unconfirmed_replaceable(self):
        credit = Credit(1, confirmed_height=None, has_replaceable_flag=True)
        assert credit.is_unconfirmed_replaceable()

    def test_is_unconfirmed_non_replaceable(self):
        credit = Credit(1, confirmed_height=None, has_replaceable_flag=False)
        assert credit.is_unconfirmed_non_replaceable()

    def test_is_unconfirmed(self):
        credit = Credit(1, confirmed_height=None, has_replaceable_flag=True)
        assert credit.is_unconfirmed()

        credit = Credit(1, confirmed_height=None, has_replaceable_flag=False)
        assert credit.is_unconfirmed()

    def test_is_confirmed(self):
        credit = Credit(1, confirmed_height=1, has_replaceable_flag=True)
        assert credit.is_confirmed()

        credit = Credit(1, confirmed_height=1, has_replaceable_flag=False)
        assert credit.is_confirmed()
