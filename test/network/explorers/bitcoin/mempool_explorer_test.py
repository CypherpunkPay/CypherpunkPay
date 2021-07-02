from test.network.explorers.bitcoin.block_explorer_test import BlockExplorerTest
from cypherpunkpay.explorers.bitcoin.mempool_explorer import MempoolExplorer


class MempoolExplorerTest(BlockExplorerTest):

    def test_get_height_mainnet_onion(self):
        be = MempoolExplorer(self.tor_http_client, btc_network='mainnet', use_tor=True)
        self.assert_btc_mainnet_height(be)

    def test_get_height_mainnet_clear(self):
        be = MempoolExplorer(self.tor_http_client, btc_network='mainnet', use_tor=False)
        self.assert_btc_mainnet_height(be)

    def test_get_height_testnet_onion(self):
        be = MempoolExplorer(self.tor_http_client, btc_network='testnet', use_tor=True)
        self.assert_btc_testnet_height(be)

    def test_get_height_testnet_clear(self):
        be = MempoolExplorer(self.tor_http_client, btc_network='testnet', use_tor=False)
        self.assert_btc_testnet_height(be)

    def test_get_address_credits_mainnet(self):
        be = MempoolExplorer(self.tor_http_client, btc_network='mainnet', use_tor=True)
        credits = be.get_address_credits(
            address='bc1qwqdg6squsna38e46795at95yu9atm8azzmyvckulcc7kytlcckxswvvzej',
            current_height=0
        )
        self.assertNotEmpty(credits.any())

    def test_get_address_credits_testnet(self):
        be = MempoolExplorer(self.tor_http_client, btc_network='testnet', use_tor=True)
        credits = be.get_address_credits(
            address='tb1q4cnvakxhuwrlfesn5uvj4haqp83t6zvpsxwzv8',
            current_height=0
        )
        self.assertEqual(1, len(credits.any()))
