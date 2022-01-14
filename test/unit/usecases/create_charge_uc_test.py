from decimal import Decimal

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
        with self.assertRaises(InvalidParams) as context:
            self.create_charge('b', 'a')
        self.assertTrue('total' in context.exception.errors)
        self.assertTrue('currency' in context.exception.errors)

    def test_valid_fiat_creates_draft_charge(self):
        charge = self.create_charge('1', 'usd')

        self.assertEqual(Decimal(1), charge.total)
        self.assertEqual('usd', charge.currency)

        self.assertTrue(charge.is_draft())
        self.assertTrue(charge.is_unpaid())

        self.assertIsNone(charge.cc_total)
        self.assertIsNone(charge.cc_currency)
        self.assertIsNone(charge.cc_address)

    def test_valid_coin_creates_awaiting_charge(self):
        charge = self.create_charge('1', 'btc')

        self.assertEqual(Decimal('1'), charge.total)
        self.assertEqual('btc', charge.currency)

        self.assertEqual(Decimal('1'), charge.cc_total)
        self.assertEqual('btc', charge.cc_currency)
        self.assertNotEmpty(charge.cc_address)

        self.assertEqual(Decimal(10_000), charge.usd_total)   # based on BTC price set in ExamplePriceTicker

        self.assertTrue(charge.is_awaiting())
        self.assertTrue(charge.is_unpaid())

    def test_valid_coin_sats_creates_awaiting_charge(self):
        charge = self.create_charge('150_000', 'sats')

        self.assertEqual(Decimal('0.00150000'), charge.total)
        self.assertEqual('btc', charge.currency)

        self.assertEqual(Decimal('0.00150000'), charge.cc_total)
        self.assertEqual('btc', charge.cc_currency)
        self.assertNotEmpty(charge.cc_address)

        self.assertTrue(charge.is_awaiting())
        self.assertTrue(charge.is_unpaid())

    def test_btc_testnet_next_address(self):
        class LocalExampleConfig(ExampleConfig):
            def btc_account_xpub(self):
                return 'vpub5UtSQhMcYBgGe3UxC5suwHbayv9Xw2raS9U4kyv5pTrikTNGLbxhBdogWm8TffqLHZhEYo7uBcouPiFQ8BNMP6JFyJmqjDxxUyToB1RcToF'

            def btc_network(self):
                return 'testnet'

        config = LocalExampleConfig()

        # First charge (pubkey derivation index 0)
        charge = self.create_charge('1', 'btc', config)
        self.assertEqual('tb1qhj6l7zh89ejysjhrlnjv6dypurlt2tz8kgg2kn', charge.cc_address)

        # Second charge (pubkey derivation index 1)
        charge = self.create_charge('1', 'btc', config)
        self.assertEqual('tb1qdl2nh30pwy8pmhxy9upue34n9r3e6dpff88e3p', charge.cc_address)

        # Third charge (pubkey derivation index 2)
        charge = self.create_charge('1', 'btc', config)
        self.assertEqual('tb1qqcc0s4hk73e4zr27w6y2m8eaz3600tpsrcupqz', charge.cc_address)

    def test_btc_mainnet_next_address(self):
        class LocalExampleConfig(ExampleConfig):
            def btc_account_xpub(self):
                return 'zpub6oMKbeQTqZyz7mbfjdSBXbHwyXYYwEN5sDSV48rLqRk6rnLELQCnnG1GqKju3DwjKX7C8MkfTWjLUPCM6RoCMnTskbvQqaDSaatwVtBQVPL'

            def btc_network(self):
                return 'mainnet'

        config = LocalExampleConfig()

        # First charge (pubkey derivation index 0)
        charge = self.create_charge(currency='btc', config=config)
        self.assertEqual('bc1q9uu4j9xgkppqx3g28ph30zrjte8fs7jaz79uf3', charge.cc_address)

        # Second charge (pubkey derivation index 1)
        charge = self.create_charge(currency='btc', config=config)
        self.assertEqual('bc1qgdmmjz44padljkvgmvfassdselctprh48tmmav', charge.cc_address)

        # Third charge (pubkey derivation index 2)
        charge = self.create_charge(currency='btc', config=config)
        self.assertEqual('bc1qfapr9g86wv4jy0l0n4zr7r6jn3tlayk2kj3ptd', charge.cc_address)

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
        charge = self.create_charge(currency='xmr', config=config)
        self.assertEqual('5BKTP2n9Tto6fJ25fv5seHUwuyiSFk2kZJV5LKnQkXp4DknK1e28tPGiEWqbLMJ4wWamGACRW7aTZEXiqEsbgJGfK2QffLz', charge.cc_address)

        # Second charge (pubkey derivation index 1)
        charge = self.create_charge(currency='xmr', config=config)
        self.assertEqual('74AVKsVDK8XPRjK6rBdwL5RVvjTgWvEudeDAcEpcVf4zYfNrDaz5K58AUbYTpUtahfNYeCnQAsebrGkevMvSeiKWNBFLdoA', charge.cc_address)

        # Third charge (pubkey derivation index 2)
        charge = self.create_charge(currency='xmr', config=config)
        self.assertEqual('75SWPExk4SoKSxTgFZfXH79bFHMkaYRiZLiCNLSZA7TrDBah2yHdkby4zfGabyNdJWez24Z1z7AznA2eK5hVReWdEH3EyFV', charge.cc_address)

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
        charge = self.create_charge(currency='xmr', config=config)
        self.assertEqual('453M2eBkgWT7P2aDsiTTzr4ohBGfCSCjnRpbQXMHjL8bRgzb6hae9UbFRg6eKF9CvKMtA8uRc9SroZHBkqzuhQB7MGAEGvP', charge.cc_address)

        # Second charge (pubkey derivation index 1)
        charge = self.create_charge(currency='xmr', config=config)
        self.assertEqual('8AN4eEYWzNEgt4VsdJFkbJe1PCgevCELQ3CypgZ9dbE6gGAyv48eo1yEuWe347u4dxMyqEdvfZ1uFNd27joS1Xr5UP93Zju', charge.cc_address)

        # Third charge (pubkey derivation index 2)
        charge = self.create_charge(currency='xmr', config=config)
        self.assertEqual('8AgpaxPWsabTwYieKdPzp8ZtrTykzVNLHLV9GmMBzV82avZ3v1V2oVYYQMYxYMoh9HQ48NdXah6vG7kCroMN8kyc2UpX8SB', charge.cc_address)

    def assertErrorOn(self, total, currency, error, config=None):
        with self.assertRaises(InvalidParams) as context:
            self.create_charge(total, currency, config=config)
        self.assertTrue(error in context.exception.errors)

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
