from cypherpunkpay.explorers.bitcoin.esplora_explorer import EsploraExplorer


class BlockstreamExplorer(EsploraExplorer):

    def api_endpoint(self) -> str:
        if self.mainnet():
            if self.use_tor():
                return 'http://explorerzydxu5ecjrkwceayqybizmpjjznk5izmitf2modhcusuqlid.onion/api'
            else:
                return 'https://blockstream.info/api'
        else:
            if self.use_tor():
                return 'http://explorerzydxu5ecjrkwceayqybizmpjjznk5izmitf2modhcusuqlid.onion//testnet/api'
            else:
                return 'https://blockstream.info/testnet/api'
