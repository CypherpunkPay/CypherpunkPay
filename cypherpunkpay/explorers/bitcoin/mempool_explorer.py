from cypherpunkpay.explorers.bitcoin.abs_esplora_explorer import AbsEsploraExplorer


class MempoolExplorer(AbsEsploraExplorer):

    def api_endpoint(self) -> str:
        if self.mainnet():
            if self.use_tor():
                return 'http://mempoolhqx4isw62xs7abwphsq7ldayuidyx2v2oethdhhj6mlo2r6ad.onion/api'
            else:
                return 'https://mempool.space/api'
        else:
            if self.use_tor():
                return 'http://mempoolhqx4isw62xs7abwphsq7ldayuidyx2v2oethdhhj6mlo2r6ad.onion/testnet/api'
            else:
                return 'https://mempool.space/testnet/api'
