from test.network.explorers.bitcoin.block_explorer_test import BlockExplorerTest
from cypherpunkpay.explorers.bitcoin.trezor_explorer import TrezorExplorer


class TrezorExplorerTest(BlockExplorerTest):

    def test_get_height_mainnet(self):
        be = TrezorExplorer(self.tor_http_client, btc_network='mainnet')
        self.assert_btc_mainnet_height(be)

    def test_get_height_testnet(self):
        be = TrezorExplorer(self.tor_http_client, btc_network='testnet')
        self.assert_btc_testnet_height(be)

    def test_get_address_credits_mainnet(self):
        be = TrezorExplorer(self.tor_http_client, btc_network='mainnet')
        credits = be.get_address_credits(
            address='bc1qwqdg6squsna38e46795at95yu9atm8azzmyvckulcc7kytlcckxswvvzej',
            current_height=0
        )
        self.assertNotEmpty(credits.all())

    def test_get_address_credits_testnet(self):
        be = TrezorExplorer(self.tor_http_client, btc_network='testnet')
        credits = be.get_address_credits(
            address='tb1q4cnvakxhuwrlfesn5uvj4haqp83t6zvpsxwzv8',
            current_height=0
        )
        self.assertEqual(1, len(credits.all()))
