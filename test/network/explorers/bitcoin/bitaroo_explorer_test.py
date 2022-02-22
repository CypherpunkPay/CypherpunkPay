from test.network.explorers.bitcoin.block_explorer_test import BlockExplorerTest
from cypherpunkpay.explorers.bitcoin.bitaroo_explorer import BitarooExplorer


class BitarooExplorerTest(BlockExplorerTest):

    def test_get_height_mainnet(self):
        be = BitarooExplorer(self.tor_http_client, btc_network='mainnet')
        self.assert_btc_mainnet_height(be)

    def test_get_address_credits_mainnet(self):
        be = BitarooExplorer(self.tor_http_client, btc_network='mainnet')
        credits = be.get_address_credits(
            address='bc1qwqdg6squsna38e46795at95yu9atm8azzmyvckulcc7kytlcckxswvvzej',
            current_height=0
        )
        self.assertNotEmpty(credits.all())
