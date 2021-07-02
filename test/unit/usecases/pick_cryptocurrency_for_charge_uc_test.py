from decimal import Decimal

import pytest

from cypherpunkpay.models.charge import Charge
from cypherpunkpay.net.http_client.dummy_http_client import DummyHttpClient
from test.unit.config.example_config import ExampleConfig
from cypherpunkpay.usecases.invalid_params import InvalidParams
from cypherpunkpay.usecases.pick_cryptocurrency_for_charge_uc import PickCryptocurrencyForChargeUC
from test.unit.db_test_case import CypherpunkpayDBTestCase
from cypherpunkpay.prices.price_tickers import ExamplePriceTickers
from test.unit.test_case import CypherpunkpayTestCase


class PickCryptocurrencyForChargeUCTest(CypherpunkpayDBTestCase):

    # ERROR HANDLING

    def test_invalid_cc_currency(self):
        charge = self.create_fiat_charge()
        with pytest.raises(InvalidParams) as c:
            self.pick_cryptocurrency_for_charge(charge, 'invalid cryptocurrency')
        assert 'cc_currency' in c.value.errors

    def test_no_cryptocurrency_wallet_configured(self):
        class LocalExampleConfig(ExampleConfig):
            def btc_account_xpub(self):
                return None
        charge = self.create_fiat_charge()
        with pytest.raises(InvalidParams) as c:
            self.pick_cryptocurrency_for_charge(charge, 'btc', config=LocalExampleConfig())
        assert 'cc_currency' in c.value.errors

    # BTC ON-CHAIN

    def test_valid__advances_charge_status(self):
        charge = self.create_charge('1', 'usd')
        self.pick_cryptocurrency_for_charge(charge, 'btc')

        assert charge.pay_status == 'unpaid'   # remains unpaid
        assert charge.status == 'awaiting'     # draft -> awaiting
        assert charge.cc_currency == 'btc'
        assert charge.usd_total == Decimal(1)  # sets usd equivalent

    def test_valid__calculates_cc_total__1usd(self):
        charge = self.create_charge('1', 'usd')
        self.pick_cryptocurrency_for_charge(charge, 'btc')

        # Assumes price $10_000 / Bitcoin  (see ExamplePriceTickers)
        assert charge.cc_total == Decimal('0.0001')

    def test_valid__calculates_cc_total__1eur(self):
        charge = self.create_charge('1.00', 'eur')
        self.pick_cryptocurrency_for_charge(charge, 'btc')

        # Assumes price $10_000 / Bitcoin and 0.9162 EUR / USD  (see ExamplePriceTickers)
        assert charge.cc_total == Decimal('0.00010915')  # 0.000109146 rounded to 8 digits of Bitcoin precision

    def test_valid__calculates_cc_total__10_000_gbp_with_rounding(self):
        charge = self.create_charge('10_000', 'gbp')
        self.pick_cryptocurrency_for_charge(charge, 'btc')

        # Assumes price $10_000 / Bitcoin and 0.7701 GBP / USD  (see ExamplePriceTickers)
        assert charge.cc_total == Decimal('1.29853266')  # 1.298532658 rounded to 8 digits of Bitcoin precision

    def test_btc_mainnet_next_address(self):
        class LocalExampleConfig(ExampleConfig):
            def btc_account_xpub(self):
                return 'zpub6oMKbeQTqZyz7mbfjdSBXbHwyXYYwEN5sDSV48rLqRk6rnLELQCnnG1GqKju3DwjKX7C8MkfTWjLUPCM6RoCMnTskbvQqaDSaatwVtBQVPL'

            def btc_network(self):
                return 'mainnet'

        config = LocalExampleConfig()

        # First charge (pubkey derivation index 0)
        charge = self.create_fiat_charge()
        self.pick_cryptocurrency_for_charge(charge, 'btc', config=config)
        assert charge.cc_address == 'bc1q9uu4j9xgkppqx3g28ph30zrjte8fs7jaz79uf3'

        # Second charge (pubkey derivation index 1)
        charge = self.create_fiat_charge()
        self.pick_cryptocurrency_for_charge(charge, 'btc', config=config)
        assert charge.cc_address == 'bc1qgdmmjz44padljkvgmvfassdselctprh48tmmav'

        # Third charge (pubkey derivation index 2)
        charge = self.create_fiat_charge()
        self.pick_cryptocurrency_for_charge(charge, 'btc', config=config)
        assert charge.cc_address == 'bc1qfapr9g86wv4jy0l0n4zr7r6jn3tlayk2kj3ptd'

    # BTC LIGHTNING

    def test_btc_lightning(self):

        class LndClientStub(object):
            def addinvoice(self, total_btc, expiry_seconds) -> str:
                return CypherpunkpayTestCase.EXAMPLE_PAYMENT_REQUEST_TESTNET

        class PickCryptocurrencyForChargeUCStub(PickCryptocurrencyForChargeUC):
            def instantiate_lnd_client(self):
                return LndClientStub()

        charge = self.create_fiat_charge()

        pick_cc = PickCryptocurrencyForChargeUCStub(
            charge=charge,
            cc_currency='btc',
            lightning=True,
            config=ExampleConfig(),
            db=self.db,
            price_tickers=ExamplePriceTickers(),
            http_client=DummyHttpClient()
        )
        pick_cc.exec()

        assert charge.cc_lightning_payment_request is not None

    # XMR ON-CHAIN

    def test_xmr_mainnet_next_address(self):
        class LocalExampleConfig(ExampleConfig):
            def xmr_main_address(self) -> str:
                return '453M2eBkgWT7P2aDsiTTzr4ohBGfCSCjnRpbQXMHjL8bRgzb6hae9UbFRg6eKF9CvKMtA8uRc9SroZHBkqzuhQB7MGAEGvP'

            def xmr_secret_view_key(self) -> str:
                return 'eca6ba6f85df40096867a44cf7b516dc754c0ad7682933188a30b93e9a32ff0c'

            def xmr_network(self):
                return 'mainnet'

        config = LocalExampleConfig()

        # First charge (pubkey derivation index 0)
        charge = self.create_fiat_charge()
        self.pick_cryptocurrency_for_charge(charge, 'xmr', config=config)
        assert charge.cc_address == '453M2eBkgWT7P2aDsiTTzr4ohBGfCSCjnRpbQXMHjL8bRgzb6hae9UbFRg6eKF9CvKMtA8uRc9SroZHBkqzuhQB7MGAEGvP'

        # Second charge (pubkey derivation index 1)
        charge = self.create_fiat_charge()
        self.pick_cryptocurrency_for_charge(charge, 'xmr', config=config)
        assert charge.cc_address == '8AN4eEYWzNEgt4VsdJFkbJe1PCgevCELQ3CypgZ9dbE6gGAyv48eo1yEuWe347u4dxMyqEdvfZ1uFNd27joS1Xr5UP93Zju'

        # Third charge (pubkey derivation index 2)
        charge = self.create_fiat_charge()
        self.pick_cryptocurrency_for_charge(charge, 'xmr', config=config)
        assert charge.cc_address == '8AgpaxPWsabTwYieKdPzp8ZtrTykzVNLHLV9GmMBzV82avZ3v1V2oVYYQMYxYMoh9HQ48NdXah6vG7kCroMN8kyc2UpX8SB'

    def create_fiat_charge(self):
        return self.create_charge('1', 'usd')

    def create_charge(self, total: [str, Decimal], currency: str):
        charge = Charge(
            total=Decimal(total),
            currency=currency,
            time_to_pay_ms=15*60*1000,
            time_to_complete_ms=15*60*1000
        )
        self.db.insert(charge)
        return charge

    def pick_cryptocurrency_for_charge(self, charge, cc_currency, config=None):
        if config is None:
            config = ExampleConfig()
        PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency=cc_currency,
            config=config,
            db=self.db,
            price_tickers=ExamplePriceTickers(),
            http_client=DummyHttpClient()
        ).exec()
