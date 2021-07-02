from test.unit.config.example_config import ExampleConfig
from cypherpunkpay.explorers.bitcoin.abs_block_explorer import AbsBlockExplorer
from cypherpunkpay.explorers.bitcoin.blockstream_explorer import BlockstreamExplorer
from cypherpunkpay.explorers.bitcoin.trezor_explorer import TrezorExplorer
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.models.credit import Credit
from test.unit.db_test_case import CypherpunkpayDBTestCase
from cypherpunkpay.net.http_client.dummy_http_client import DummyHttpClient
from cypherpunkpay.usecases.fetch_address_credits_from_explorers_uc import FetchAddressCreditsFromExplorersUC


class StubBlockExplorer(AbsBlockExplorer):

    def __init__(self, address_credits: [AddressCredits, None]):
        super().__init__(DummyHttpClient())
        self._mock_address_credits = address_credits

    def get_height(self) -> [int, None]:
        return None

    def get_address_credits(self, address: str, current_height: int) -> [AddressCredits, None]:
        return self._mock_address_credits

    def api_endpoint(self) -> str:
        pass


class StubFetchAddressCreditsFromExplorersUC(FetchAddressCreditsFromExplorersUC):

    def __init__(self, address_credits_1, address_credits_2):
        super().__init__(
            'btc',
            'bc1quwtrymfzavun8awsv9fqv36wlk0058puuw7mer',
            'cypherpunkpay.explorers.bitcoin.some_exmplorer SomeExplorer',
            'cypherpunkpay.explorers.bitcoin.another_explorer AnotherExplorer',
            1000,
            DummyHttpClient(),
            config=ExampleConfig()
        )
        self.stub_address_credits_1 = address_credits_1
        self.stub_address_credits_2 = address_credits_2

    def _instantiate_block_explorers(self):
        self.block_explorer_1 = StubBlockExplorer(self.stub_address_credits_1)
        self.block_explorer_2 = StubBlockExplorer(self.stub_address_credits_2)


class FetchAddressCreditsFromExplorersUCTest(CypherpunkpayDBTestCase):

    def test_instantiates_block_explorers(self):
        uc = FetchAddressCreditsFromExplorersUC(
            'btc',
            'bc1quwtrymfzavun8awsv9fqv36wlk0058puuw7mer',
            'cypherpunkpay.explorers.bitcoin.blockstream_explorer BlockstreamExplorer',
            'cypherpunkpay.explorers.bitcoin.trezor_explorer TrezorExplorer',
            1000,
            DummyHttpClient(),
            config=ExampleConfig()
        )
        uc._instantiate_block_explorers()
        self.assertIsInstance(uc.block_explorer_1, BlockstreamExplorer)
        self.assertIsInstance(uc.block_explorer_2, TrezorExplorer)

    def test_when_first_None__return_None(self):
        address_credits = StubFetchAddressCreditsFromExplorersUC(
            None,
            AddressCredits([Credit(1, None, False)], 2000)
        ).exec()
        self.assertIsNone(address_credits)

    def test_when_last_None__return_None(self):
        address_credits = StubFetchAddressCreditsFromExplorersUC(
            AddressCredits([Credit(1, None, False)], 2000),
            None
        ).exec()
        self.assertIsNone(address_credits)

    def test_when_discrepancy__return_None(self):
        address_credits = StubFetchAddressCreditsFromExplorersUC(
            AddressCredits([Credit(1, None, False), Credit(2, None, False)], 2000),
            AddressCredits([Credit(1, None, False)], 2000)
        ).exec()
        self.assertIsNone(address_credits)

    def test_when_both_empty__return_empty_credits(self):
        address_credits = StubFetchAddressCreditsFromExplorersUC(
            AddressCredits([], 1000),
            AddressCredits([], 1000)
        ).exec()
        self.assertTrue(address_credits)
        self.assertEqual([], address_credits.any())
        self.assertEqual(1000, address_credits.blockchain_height())

    def test_when_both_same__return_credits(self):
        address_credits = StubFetchAddressCreditsFromExplorersUC(
            AddressCredits([Credit(1, None, False)], 2000),
            AddressCredits([Credit(1, None, False)], 2000)
        ).exec()
        self.assertTrue(address_credits)
        self.assertEqual(1, len(address_credits.any()))
        self.assertEqual(2000, address_credits.blockchain_height())

    def test_when_both_same_except_order__return_credits(self):
        address_credits = StubFetchAddressCreditsFromExplorersUC(
            AddressCredits([Credit(1, None, False), Credit(2, None, False)], 2000),
            AddressCredits([Credit(2, None, False), Credit(1, None, False)], 2000)
        ).exec()
        self.assertTrue(address_credits)
        self.assertEqual(2, len(address_credits.any()))
        self.assertEqual(2000, address_credits.blockchain_height())
