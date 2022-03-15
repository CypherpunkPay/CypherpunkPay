from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.models.credit import Credit

from test.unit.test_case import CypherpunkpayTestCase


class AddressCreditsTest(CypherpunkpayTestCase):

    def test_any(self):
        account_credits = AddressCredits([
            Credit(1, 1, True),
            Credit(1, 1, False),
            Credit(1, None, True),
            Credit(1, None, False)
        ], 1)
        assert len(account_credits.all()) == 4

    def test_unconfirmed_replaceable(self):
        account_credits = AddressCredits([
            Credit(1, confirmed_height=1, has_replaceable_flag=True),
            Credit(1, confirmed_height=1, has_replaceable_flag=False),
            Credit(1, confirmed_height=None, has_replaceable_flag=True),
            Credit(50, confirmed_height=None, has_replaceable_flag=True),
            Credit(1, confirmed_height=None, has_replaceable_flag=False)
        ], 1)
        assert len(account_credits.unconfirmed_replaceable()) == 2

    def test_unconfirmed_non_replaceable(self):
        account_credits = AddressCredits([
            Credit(1, confirmed_height=1, has_replaceable_flag=True),
            Credit(1, confirmed_height=1, has_replaceable_flag=False),
            Credit(1, confirmed_height=None, has_replaceable_flag=True),
            Credit(1, confirmed_height=None, has_replaceable_flag=False),
            Credit(50, confirmed_height=None, has_replaceable_flag=False)
        ], 1)
        assert len(account_credits.unconfirmed_non_replaceable()) == 2

    def test_confirmed_1(self):
        account_credits = AddressCredits([
            Credit(1, confirmed_height=1000, has_replaceable_flag=True),
            Credit(1, confirmed_height=1001, has_replaceable_flag=True),
            Credit(1, confirmed_height=1002, has_replaceable_flag=True),
            Credit(1, confirmed_height=None, has_replaceable_flag=True),
            Credit(1, confirmed_height=None, has_replaceable_flag=False)
        ], 1002)
        assert len(account_credits.confirmed_1()) == 3

    def test_confirmed_n(self):
        account_credits = AddressCredits([
            Credit(1, confirmed_height=1000, has_replaceable_flag=True),
            Credit(1, confirmed_height=1001, has_replaceable_flag=True),
            Credit(1, confirmed_height=1002, has_replaceable_flag=True),
            Credit(1, confirmed_height=None, has_replaceable_flag=True),
            Credit(1, confirmed_height=None, has_replaceable_flag=False)
        ], 1002)
        assert len(account_credits.confirmed_n(2)) == 2

    def test_equal(self):
        # equal / empty
        assert AddressCredits([], 0) == AddressCredits([], 0)

        # equal / same single Credit
        ac1 = AddressCredits([Credit(1, confirmed_height=1000, has_replaceable_flag=True)], 900)
        ac2 = AddressCredits([Credit(1, confirmed_height=1000, has_replaceable_flag=True)], 900)
        assert ac1 == ac2

        # equal / same two Credits but different order
        ac1 = AddressCredits([Credit(1, confirmed_height=1000, has_replaceable_flag=True), Credit(2, confirmed_height=1000, has_replaceable_flag=True)], 900)
        ac2 = AddressCredits([Credit(2, confirmed_height=1000, has_replaceable_flag=True), Credit(1, confirmed_height=1000, has_replaceable_flag=True)], 900)
        assert ac1 == ac2

        # different size
        ac1 = AddressCredits([Credit(1, confirmed_height=1000, has_replaceable_flag=True)], 900)
        ac2 = AddressCredits([Credit(1, confirmed_height=1000, has_replaceable_flag=True), Credit(1, confirmed_height=1000, has_replaceable_flag=True)], 900)
        assert ac1 != ac2

        # different block height
        ac1 = AddressCredits([Credit(1, confirmed_height=1000, has_replaceable_flag=True)], 901)
        ac2 = AddressCredits([Credit(1, confirmed_height=1000, has_replaceable_flag=True)], 900)
        assert ac1 != ac2

        # different amount
        ac1 = AddressCredits([Credit(1, confirmed_height=1000, has_replaceable_flag=True)], 900)
        ac2 = AddressCredits([Credit(2, confirmed_height=1000, has_replaceable_flag=True)], 900)
        assert ac1 != ac2

        # different confirmed height
        ac1 = AddressCredits([Credit(1, confirmed_height=1000, has_replaceable_flag=True)], 900)
        ac2 = AddressCredits([Credit(1, confirmed_height=1001, has_replaceable_flag=True)], 900)
        assert ac1 != ac2

        # # different RBF flag
        # ac1 = AddressCredits([Credit(1, confirmed_height=1000, has_replaceable_flag=True)], 900)
        # ac2 = AddressCredits([Credit(1, confirmed_height=1000, has_replaceable_flag=False)], 900)
        # self.assertTrue(ac1 != ac2)
