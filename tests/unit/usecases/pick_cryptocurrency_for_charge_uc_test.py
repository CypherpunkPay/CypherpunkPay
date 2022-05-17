from decimal import Decimal

import pytest

from cypherpunkpay.ln.lightning_dummy_client import LightningDummyClient
from cypherpunkpay.models.charge import Charge
from tests.unit.config.example_config import ExampleConfig
from cypherpunkpay.usecases.invalid_params import InvalidParams
from cypherpunkpay.usecases.pick_cryptocurrency_for_charge_uc import PickCryptocurrencyForChargeUC
from tests.unit.db_test_case import CypherpunkpayDBTestCase
from cypherpunkpay.prices.price_tickers import ExamplePriceTickers
from tests.unit.test_case import CypherpunkpayTestCase


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

        class LocalExampleConfigWithOffset(ExampleConfig):
            def btc_account_xpub(self):
                return 'zpub6oMKbeQTqZyz7mbfjdSBXbHwyXYYwEN5sDSV48rLqRk6rnLELQCnnG1GqKju3DwjKX7C8MkfTWjLUPCM6RoCMnTskbvQqaDSaatwVtBQVPL'

            def btc_network(self):
                return 'mainnet'

            def btc_account_offset(self):
                return -1

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

        # Fourth charge (pubkey derivation index 3 - 1 (offset) = 2)
        config_with_offset = LocalExampleConfigWithOffset()
        charge = self.create_fiat_charge()
        self.pick_cryptocurrency_for_charge(charge, 'btc', config=config_with_offset)
        assert charge.cc_address == 'bc1qfapr9g86wv4jy0l0n4zr7r6jn3tlayk2kj3ptd'  # again, because -1 offset

    def test_btc_testnet_next_address(self):
        class LocalExampleConfig(ExampleConfig):
            def btc_account_xpub(self):
                return 'vpub5UtSQhMcYBgGe3UxC5suwHbayv9Xw2raS9U4kyv5pTrikTNGLbxhBdogWm8TffqLHZhEYo7uBcouPiFQ8BNMP6JFyJmqjDxxUyToB1RcToF'

            def btc_network(self):
                return 'testnet'

        config = LocalExampleConfig()

        # First charge (pubkey derivation index 0)
        charge = self.create_fiat_charge()
        self.pick_cryptocurrency_for_charge(charge, 'btc', config=config)
        self.assertEqual('tb1qhj6l7zh89ejysjhrlnjv6dypurlt2tz8kgg2kn', charge.cc_address)

        # Second charge (pubkey derivation index 1)
        charge = self.create_fiat_charge()
        self.pick_cryptocurrency_for_charge(charge, 'btc', config=config)
        self.assertEqual('tb1qdl2nh30pwy8pmhxy9upue34n9r3e6dpff88e3p', charge.cc_address)

        # Third charge (pubkey derivation index 2)
        charge = self.create_fiat_charge()
        self.pick_cryptocurrency_for_charge(charge, 'btc', config=config)
        self.assertEqual('tb1qqcc0s4hk73e4zr27w6y2m8eaz3600tpsrcupqz', charge.cc_address)

    # BTC LIGHTNING

    def test_btc_lightning(self):

        class LightningClientStub(LightningDummyClient):
            def create_invoice(self, total_btc: [Decimal, None] = None, memo: str = None, expiry_seconds: [int, None] = None) -> str:
                return CypherpunkpayTestCase.EXAMPLE_PAYMENT_REQUEST_TESTNET

        charge = self.create_fiat_charge()

        pick_cc = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='btc',
            lightning=True,
            config=ExampleConfig(),
            db=self.db,
            price_tickers=ExamplePriceTickers(),
            ln_client=LightningClientStub()
        )
        pick_cc.exec()

        self.assertIsNotNone(charge.cc_lightning_payment_request)

    def test_btc_lightning_sats(self):

        class LightningClientStub(LightningDummyClient):
            def create_invoice(self, total_btc: [Decimal, None] = None, memo: str = None, expiry_seconds: [int, None] = None) -> str:
                return CypherpunkpayTestCase.EXAMPLE_PAYMENT_REQUEST_TESTNET

        charge = self.create_charge('123', 'sats')

        pick_cc = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='btc',
            lightning=True,
            config=ExampleConfig(),
            db=self.db,
            price_tickers=ExamplePriceTickers(),
            ln_client=LightningClientStub()
        )
        pick_cc.exec()

        self.assertIsNotNone(charge.cc_lightning_payment_request)
        self.assertEqual(charge.cc_currency, 'btc')
        self.assertEqual(charge.cc_total, Decimal('0.00000123'))

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

    def test_xmr_stagenet_next_address(self):
        class LocalExampleConfig(ExampleConfig):
            def xmr_main_address(self) -> str:
                return '5BKTP2n9Tto6fJ25fv5seHUwuyiSFk2kZJV5LKnQkXp4DknK1e28tPGiEWqbLMJ4wWamGACRW7aTZEXiqEsbgJGfK2QffLz'

            def xmr_secret_view_key(self) -> str:
                return '1543738e3ff094c144ed6697a26beb313c765ffd368b781bd4602a4c6153c305'

            def xmr_network(self):
                return 'stagenet'

        config = LocalExampleConfig()

        # First charge (pubkey derivation index 0)
        charge = self.create_fiat_charge()
        self.pick_cryptocurrency_for_charge(charge, 'xmr', config=config)
        self.assertEqual('5BKTP2n9Tto6fJ25fv5seHUwuyiSFk2kZJV5LKnQkXp4DknK1e28tPGiEWqbLMJ4wWamGACRW7aTZEXiqEsbgJGfK2QffLz', charge.cc_address)

        # Second charge (pubkey derivation index 1)
        charge = self.create_fiat_charge()
        self.pick_cryptocurrency_for_charge(charge, 'xmr', config=config)
        self.assertEqual('74AVKsVDK8XPRjK6rBdwL5RVvjTgWvEudeDAcEpcVf4zYfNrDaz5K58AUbYTpUtahfNYeCnQAsebrGkevMvSeiKWNBFLdoA', charge.cc_address)

        # Third charge (pubkey derivation index 2)
        charge = self.create_fiat_charge()
        self.pick_cryptocurrency_for_charge(charge, 'xmr', config=config)
        self.assertEqual('75SWPExk4SoKSxTgFZfXH79bFHMkaYRiZLiCNLSZA7TrDBah2yHdkby4zfGabyNdJWez24Z1z7AznA2eK5hVReWdEH3EyFV', charge.cc_address)

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
            lightning=False,
            config=config,
            db=self.db,
            price_tickers=ExamplePriceTickers()
        ).exec()
