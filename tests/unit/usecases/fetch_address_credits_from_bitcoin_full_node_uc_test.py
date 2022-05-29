from cypherpunkpay.net.http_client.dummy_http_client import DummyHttpClient
from cypherpunkpay.usecases.fetch_address_credits_from_bitcoin_full_node_uc import FetchAddressCreditsFromBitcoinFullNodeUC
from tests.unit.config.example_config import ExampleConfig
from tests.unit.db_test_case import CypherpunkpayDBTestCase


class FetchAddressCreditsFromBitcoinFullNodeUCTest(CypherpunkpayDBTestCase):

    ANY_TESTNET_ADDRESS = '2MuszDiNxWDDNb2mi2PMyyAsgsFXf5zDet5'
    ANY_WALLET_FINGERPRINT = ''
    ANY_HEIGHT = 2**31

    # No need to test logic because it is just a pass through class, existing for layers consistency.
    # See tests for BitcoinCoreClient instead.

    def test_returns_None_on_error(self):
        uc = FetchAddressCreditsFromBitcoinFullNodeUC(
            address=self.ANY_TESTNET_ADDRESS,
            wallet_fingerprint=self.ANY_WALLET_FINGERPRINT,
            current_height=self.ANY_HEIGHT,
            http_client=DummyHttpClient(),  # will raise RequestException
            config=ExampleConfig()
        )
        ret = uc.exec()
        assert ret is None
