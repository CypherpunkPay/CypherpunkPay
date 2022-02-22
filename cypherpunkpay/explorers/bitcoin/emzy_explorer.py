from cypherpunkpay.exceptions import UnsupportedNetwork
from cypherpunkpay.explorers.bitcoin.esplora_explorer import EsploraExplorer


class EmzyExplorer(EsploraExplorer):

    def api_endpoint(self) -> str:
        if self.mainnet():
            if self.use_tor():
                return 'http://mempool4t6mypeemozyterviq3i5de4kpoua65r3qkn5i3kknu5l2cad.onion/api'
            else:
                return 'https://mempool.emzy.de/api'
        else:
            raise UnsupportedNetwork()
