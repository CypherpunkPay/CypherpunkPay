from decimal import Decimal

from cypherpunkpay.net.http_client.dummy_http_client import DummyHttpClient
from test.unit.cypherpunkpay.app.example_config import ExampleConfig
from cypherpunkpay.usecases.create_charge_uc import CreateChargeUC
from cypherpunkpay.usecases.invalid_params import InvalidParams
from cypherpunkpay.usecases.pick_cryptocurrency_for_charge_uc import PickCryptocurrencyForChargeUC
from test.unit.cypherpunkpay.cypherpunkpay_db_test_case import CypherpunkpayDBTestCase
from cypherpunkpay.prices.price_tickers import ExamplePriceTickers


class PickCryptocurrencyForChargeUCTest(CypherpunkpayDBTestCase):

    def test_invalid_cc_currency(self):
        charge = self.create_charge('1', 'usd')
        with self.assertRaises(InvalidParams) as context:
            self.pick_cryptocurrency_for_charge(charge, 'invalid cryptocurrency')
        self.assertTrue('cc_currency' in context.exception.errors)

    def test_no_cryptocurrency_wallet_configured(self):
        class LocalExampleConfig(ExampleConfig):
            def btc_account_xpub(self):
                return None
        charge = self.create_charge('1', 'usd')
        with self.assertRaises(InvalidParams) as context:
            self.pick_cryptocurrency_for_charge(charge, 'btc', config=LocalExampleConfig())
        self.assertTrue('cc_currency' in context.exception.errors)

    def test_valid__advances_charge_status(self):
        charge = self.create_charge('1', 'usd')
        self.pick_cryptocurrency_for_charge(charge, 'btc')

        self.assertEqual('unpaid', charge.pay_status)   # remains unpaid
        self.assertEqual('awaiting', charge.status)     # draft -> awaiting
        self.assertEqual('btc', charge.cc_currency)
        self.assertEqual(Decimal(1), charge.usd_total)  # sets usd equivalent
        self.assertIsNotNone(charge.cc_address)

    def test_valid__calculates_cc_total__1usd(self):
        charge = self.create_charge('1', 'usd')
        self.pick_cryptocurrency_for_charge(charge, 'btc')

        # Assumes price $10_000 / Bitcoin  (see ExamplePriceTickers)
        self.assertEqual(Decimal('0.0001'), charge.cc_total)

    def test_valid__calculates_cc_total__1eur(self):
        charge = self.create_charge('1.00', 'eur')
        self.pick_cryptocurrency_for_charge(charge, 'btc')

        # Assumes price $10_000 / Bitcoin and 0.9162 EUR / USD  (see ExamplePriceTickers)
        self.assertEqual(Decimal('0.00010915'), charge.cc_total)  # 0.000109146 rounded to 8 digits of Bitcoin precision

    def test_valid__calculates_cc_total__10_000_gbp_with_rounding(self):
        charge = self.create_charge('10_000', 'gbp')
        self.pick_cryptocurrency_for_charge(charge, 'btc')

        # Assumes price $10_000 / Bitcoin and 0.7701 GBP / USD  (see ExamplePriceTickers)
        self.assertEqual(Decimal('1.29853266'), charge.cc_total)  # 1.298532658 rounded to 8 digits of Bitcoin precision

    def test_btc_mainnet_next_address(self):
        class LocalExampleConfig(ExampleConfig):
            def btc_account_xpub(self):
                return 'zpub6oMKbeQTqZyz7mbfjdSBXbHwyXYYwEN5sDSV48rLqRk6rnLELQCnnG1GqKju3DwjKX7C8MkfTWjLUPCM6RoCMnTskbvQqaDSaatwVtBQVPL'

            def btc_network(self):
                return 'mainnet'

        config = LocalExampleConfig()

        # First charge (pubkey derivation index 0)
        charge = self.create_fiat_charge(config)
        self.pick_cryptocurrency_for_charge(charge, 'btc', config=config)
        self.assertEqual('bc1q9uu4j9xgkppqx3g28ph30zrjte8fs7jaz79uf3', charge.cc_address)

        # Second charge (pubkey derivation index 1)
        charge = self.create_fiat_charge(config)
        self.pick_cryptocurrency_for_charge(charge, 'btc', config=config)
        self.assertEqual('bc1qgdmmjz44padljkvgmvfassdselctprh48tmmav', charge.cc_address)

        # Third charge (pubkey derivation index 2)
        charge = self.create_fiat_charge(config)
        self.pick_cryptocurrency_for_charge(charge, 'btc', config=config)
        self.assertEqual('bc1qfapr9g86wv4jy0l0n4zr7r6jn3tlayk2kj3ptd', charge.cc_address)

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
        charge = self.create_fiat_charge(config)
        self.pick_cryptocurrency_for_charge(charge, 'xmr', config=config)
        self.assertEqual('453M2eBkgWT7P2aDsiTTzr4ohBGfCSCjnRpbQXMHjL8bRgzb6hae9UbFRg6eKF9CvKMtA8uRc9SroZHBkqzuhQB7MGAEGvP', charge.cc_address)

        # Second charge (pubkey derivation index 1)
        charge = self.create_fiat_charge(config)
        self.pick_cryptocurrency_for_charge(charge, 'xmr', config=config)
        self.assertEqual('8AN4eEYWzNEgt4VsdJFkbJe1PCgevCELQ3CypgZ9dbE6gGAyv48eo1yEuWe347u4dxMyqEdvfZ1uFNd27joS1Xr5UP93Zju', charge.cc_address)

        # Third charge (pubkey derivation index 2)
        charge = self.create_fiat_charge(config)
        self.pick_cryptocurrency_for_charge(charge, 'xmr', config=config)
        self.assertEqual('8AgpaxPWsabTwYieKdPzp8ZtrTykzVNLHLV9GmMBzV82avZ3v1V2oVYYQMYxYMoh9HQ48NdXah6vG7kCroMN8kyc2UpX8SB', charge.cc_address)

    def create_fiat_charge(self, config):
        return self.create_charge('1', 'usd', config=config)

    def create_charge(self, total: [str, Decimal], currency='btc', config=None):
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
