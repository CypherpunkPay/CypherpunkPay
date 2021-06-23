from cypherpunkpay.explorers.bitcoin.abs_esplora_explorer import AbsEsploraExplorer


class BlockstreamExplorer(AbsEsploraExplorer):

    def api_endpoint(self) -> str:
        if self.mainnet():
            if self.use_tor():
                return 'http://explorernuoc63nb.onion/api'
            else:
                return 'https://blockstream.info/api'
        else:
            if self.use_tor():
                return 'http://explorernuoc63nb.onion/testnet/api'
            else:
                return 'https://blockstream.info/testnet/api'
