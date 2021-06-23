from cypherpunkpay.common import *
from test.internet.cypherpunkpay.cypherpunkpay_network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.explorers.bitcoin.abs_block_explorer import AbsBlockExplorer


class BlockExplorerTest(CypherpunkpayNetworkTestCase):

    def assert_btc_mainnet_height(self, be: AbsBlockExplorer):
        height = be.get_height()
        self.assertIsNotNone(height)
        self.assertGreater(height, 678444)
        self.assertLess(height, 1000000)

    def assert_btc_testnet_height(self, be: AbsBlockExplorer):
        height = be.get_height()
        self.assertIsNotNone(height)
        self.assertGreater(height, 1940613)
        self.assertLess(height, 3000000)
