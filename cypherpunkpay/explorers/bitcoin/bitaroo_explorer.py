from cypherpunkpay.exceptions import UnsupportedNetwork
from cypherpunkpay.explorers.bitcoin.abs_esplora_explorer import AbsEsploraExplorer


class BitarooExplorer(AbsEsploraExplorer):

    def api_endpoint(self) -> str:
        if self.mainnet():
            return 'https://mempool.bitaroo.net/api'
        else:
            raise UnsupportedNetwork()
