from cypherpunkpay.exceptions import UnsupportedNetwork
from cypherpunkpay.explorers.bitcoin.esplora_explorer import EsploraExplorer


class BitarooExplorer(EsploraExplorer):

    def api_endpoint(self) -> str:
        if self.mainnet():
            return 'https://mempool.bitaroo.net/api'
        else:
            raise UnsupportedNetwork()
