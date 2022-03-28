from decimal import Decimal

import pytest

from cypherpunkpay.usecases.invalid_params import InvalidParams
from test.unit.config.example_config import ExampleConfig
from cypherpunkpay.usecases.create_charge_uc import CreateChargeUC
from test.unit.db_test_case import CypherpunkpayDBTestCase
from cypherpunkpay.prices.price_tickers import ExamplePriceTickers


class CreateChargeUCTest(CypherpunkpayDBTestCase):

    def test_invalid_total(self):
        self.assertErrorOn('', 'usd', error='total')

        self.assertErrorOn('1a', 'usd', error='total')
        self.assertErrorOn('1 a', 'usd', error='total')
        self.assertErrorOn('a 1', 'usd', error='total')
        self.assertErrorOn('1,1', 'usd', error='total')

        self.assertErrorOn('-1', 'usd', error='total')
        self.assertErrorOn('0', 'usd', error='total')

        # Sub-penny fiat amounts disallowed
        self.assertErrorOn('0.009', 'chf', error='total')
        # Sub-satoshi for any cryptocurrency disallowed due to database precision of 8 decimal points
        self.assertErrorOn('0.0000000099', 'btc', error='total')
        self.assertErrorOn('0.0000000099', 'xmr', error='total')

    def test_invalid_currency(self):
        self.assertErrorOn('1', '', error='currency')
        self.assertErrorOn('1', 'bcash', error='currency')
        self.assertErrorOn('1', 'BCH', error='currency')
        self.assertErrorOn('1', 'cypherpunkpay', error='currency')
        self.assertErrorOn('1', 'cypherpunkpay', error='currency')

    def test_no_cryptocurrency_wallet_configured(self):
        class LocalExampleConfig(ExampleConfig):
            def btc_account_xpub(self):
                return None
        self.assertErrorOn('1', 'btc', error='currency', config=LocalExampleConfig())

    def test_invalid_both(self):
        with pytest.raises(InvalidParams) as context:
            self.create_charge('b', 'a')
            assert 'total' in str(context.value)
            assert 'currency' in str(context.value)

    def test_valid_fiat_creates_draft_charge(self):
        charge = self.create_charge('1', 'usd')

        assert charge.total == Decimal(1)
        assert charge.currency == 'usd'

        assert charge.is_draft()
        assert charge.is_unpaid()

        assert charge.cc_total is None
        assert charge.cc_currency is None
        assert charge.cc_address is None

    def test_valid_coin_creates_draft_charge(self):
        charge = self.create_charge('1', 'btc')

        assert charge.total == Decimal('1')
        assert charge.currency == 'btc'

        assert charge.cc_total is None
        assert charge.cc_currency is None

        assert charge.is_draft()
        assert charge.is_unpaid()

    def test_valid_coin_sats_creates_draft_charge(self):
        charge = self.create_charge('150_000', 'sats')

        assert charge.total == Decimal('150_000')
        assert charge.currency == 'sats'

        assert charge.cc_total is None
        assert charge.cc_currency is None

        assert charge.is_draft()
        assert charge.is_unpaid()

    def assertErrorOn(self, total, currency, error, config=None):
        with pytest.raises(InvalidParams) as context:
            self.create_charge(total, currency, config=config)
        print(context.__dict__)
        assert error in str(context.value)

    def create_charge(self, total: [str, Decimal] = '1', currency='btc', config=None):
        if config is None:
            config = ExampleConfig()
        return CreateChargeUC(
            total,
            currency,
            config=config,
            db=self.db,
            price_tickers=ExamplePriceTickers(),
            qr_cache={}
        ).exec()
