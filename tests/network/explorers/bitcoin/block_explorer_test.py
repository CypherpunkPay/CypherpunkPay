from tests.network.network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.explorers.bitcoin.block_explorer import BlockExplorer


class BlockExplorerTest(CypherpunkpayNetworkTestCase):

    def assert_btc_mainnet_height(self, be: BlockExplorer):
        height = be.get_height()
        self.assertIsNotNone(height)
        self.assertGreater(height, 678444)
        self.assertLess(height, 1000000)

    def assert_btc_testnet_height(self, be: BlockExplorer):
        height = be.get_height()
        self.assertIsNotNone(height)
        self.assertGreater(height, 1940613)
        self.assertLess(height, 3000000)
