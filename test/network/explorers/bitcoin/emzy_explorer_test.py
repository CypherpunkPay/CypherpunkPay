from test.network.explorers.bitcoin.block_explorer_test import BlockExplorerTest
from cypherpunkpay.explorers.bitcoin.emzy_explorer import EmzyExplorer


class EmzyExplorerTest(BlockExplorerTest):

    def test_get_height_mainnet_onion(self):
        be = EmzyExplorer(self.tor_http_client, btc_network='mainnet', use_tor=True)
        self.assert_btc_mainnet_height(be)

    def test_get_height_mainnet_clear(self):
        be = EmzyExplorer(self.tor_http_client, btc_network='mainnet', use_tor=False)
        self.assert_btc_mainnet_height(be)

    def test_get_address_credits_mainnet(self):
        be = EmzyExplorer(self.tor_http_client, btc_network='mainnet', use_tor=True)
        credits = be.get_address_credits(
            address='bc1qwqdg6squsna38e46795at95yu9atm8azzmyvckulcc7kytlcckxswvvzej',
            current_height=0
        )
        self.assertNotEmpty(credits.any())
