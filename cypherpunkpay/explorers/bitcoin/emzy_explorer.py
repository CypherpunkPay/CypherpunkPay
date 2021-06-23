from cypherpunkpay.exceptions import UnsupportedNetwork
from cypherpunkpay.explorers.bitcoin.abs_esplora_explorer import AbsEsploraExplorer


class EmzyExplorer(AbsEsploraExplorer):

    def api_endpoint(self) -> str:
        if self.mainnet():
            if self.use_tor():
                return 'http://mempool4t6mypeemozyterviq3i5de4kpoua65r3qkn5i3kknu5l2cad.onion/api'
            else:
                return 'https://mempool.emzy.de/api'
        else:
            raise UnsupportedNetwork()
