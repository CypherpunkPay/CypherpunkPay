from cypherpunkpay.explorers.bitcoin.bitaps_explorer import BitapsExplorer
from cypherpunkpay.explorers.bitcoin.bitaroo_explorer import BitarooExplorer
from cypherpunkpay.explorers.bitcoin.blockstream_explorer import BlockstreamExplorer
from cypherpunkpay.explorers.bitcoin.emzy_explorer import EmzyExplorer
from cypherpunkpay.explorers.bitcoin.mempool_explorer import MempoolExplorer
from cypherpunkpay.explorers.bitcoin.trezor_explorer import TrezorExplorer
from cypherpunkpay.exceptions import UnsupportedNetwork, UnsupportedCoin


class SupportedExplorers(object):

    BTC_MAINNET = [
        BitapsExplorer,
        BlockstreamExplorer,
        BitarooExplorer,
        EmzyExplorer,
        MempoolExplorer,
        TrezorExplorer,
    ]

    BTC_TESTNET = [
        BitapsExplorer,
        BlockstreamExplorer,
        MempoolExplorer,
        TrezorExplorer,
    ]

    XMR_MAINNET = []
    XMR_STAGENET = []

    def get(self, coin: str, network: str):
        if coin == 'btc':
            if network == 'mainnet':
                return self.BTC_MAINNET
            if network == 'testnet':
                return self.BTC_TESTNET
            raise UnsupportedNetwork(network)

        if coin == 'xmr':
            if network == 'mainnet':
                return self.XMR_MAINNET
            if network == 'stagenet':
                return self.XMR_STAGENET
            raise UnsupportedNetwork(network)

        raise UnsupportedCoin(coin)
