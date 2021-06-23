from statistics import median_low

from cypherpunkpay.common import *
from cypherpunkpay.app import App
from cypherpunkpay.explorers.bitcoin.bitaps_explorer import BitapsExplorer
from cypherpunkpay.explorers.bitcoin.bitaroo_explorer import BitarooExplorer
from cypherpunkpay.explorers.bitcoin.blockstream_explorer import BlockstreamExplorer
from cypherpunkpay.explorers.bitcoin.emzy_explorer import EmzyExplorer
from cypherpunkpay.explorers.bitcoin.mempool_explorer import MempoolExplorer
from cypherpunkpay.explorers.bitcoin.trezor_explorer import TrezorExplorer
from cypherpunkpay.exceptions import UnsupportedCoin
from cypherpunkpay.full_node_clients.bitcoin_core_client import BitcoinCoreClient
from cypherpunkpay.full_node_clients.json_rpc_client import JsonRpcError
from cypherpunkpay.usecases import UseCase


class FetchBlockchainHeightUC(UseCase):

    def __init__(self, coin, config=None, http_client=None):
        self.coin = coin
        self.config = config if config else App().config()
        self.http_client = http_client if http_client else App().http_client()

    def exec(self) -> [int, None]:
        if self.coin == 'btc':
            if self.config.btc_node_enabled():
                return self.btc_height_from_node()
            else:
                return self.btc_height_from_explorers()
        elif self.coin == 'xmr':
            # TODO: implement
            return 1
        else:
            raise UnsupportedCoin(self.coin)

    def btc_height_from_explorers(self) -> [int, None]:
        if self.config.btc_mainnet():
            btc_heights = list(filter(None, [
                BlockstreamExplorer(http_client=self.http_client, btc_network=self.config.btc_network(), use_tor=self.config.use_tor()).get_height(),
                TrezorExplorer(http_client=self.http_client, btc_network=self.config.btc_network(), use_tor=self.config.use_tor()).get_height(),
                BitapsExplorer(http_client=self.http_client, btc_network=self.config.btc_network(), use_tor=self.config.use_tor()).get_height(),
                MempoolExplorer(http_client=self.http_client, btc_network=self.config.btc_network(), use_tor=self.config.use_tor()).get_height(),
                EmzyExplorer(http_client=self.http_client, btc_network=self.config.btc_network(), use_tor=self.config.use_tor()).get_height(),
                BitarooExplorer(http_client=self.http_client, btc_network=self.config.btc_network(), use_tor=self.config.use_tor()).get_height()
            ]))
        else:
            # Some explorers do not support testnet
            btc_heights = list(filter(None, [
                BlockstreamExplorer(http_client=self.http_client, btc_network=self.config.btc_network(), use_tor=self.config.use_tor()).get_height(),
                TrezorExplorer(http_client=self.http_client, btc_network=self.config.btc_network(), use_tor=self.config.use_tor()).get_height(),
                BitapsExplorer(http_client=self.http_client, btc_network=self.config.btc_network(), use_tor=self.config.use_tor()).get_height(),
                MempoolExplorer(http_client=self.http_client, btc_network=self.config.btc_network(), use_tor=self.config.use_tor()).get_height(),
            ]))
        if len(btc_heights) > 0:
            return median_low(btc_heights)
        return None

    def btc_height_from_node(self) -> [int, None]:
        try:
            return BitcoinCoreClient(
                url=self.config.btc_node_rpc_url(),
                rpc_user=self.config.btc_node_rpc_user(),
                rpc_password=self.config.btc_node_rpc_password(),
                http_client=self.http_client
            ).get_height()
        except JsonRpcError:
            return None  # The exception has been logged upstream. The action will be retried. Safe to swallow.
