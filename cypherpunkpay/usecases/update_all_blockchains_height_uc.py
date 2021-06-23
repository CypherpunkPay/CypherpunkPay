from cypherpunkpay.app import App
from cypherpunkpay.common import *
from cypherpunkpay.usecases import UseCase
from cypherpunkpay.usecases.fetch_blockchain_height_uc import FetchBlockchainHeightUC


class UpdateAllBlockchainsHeightUC(UseCase):

    def __init__(self, config=None, http_client=None, db=None):
        self._config = config if config else App().config()
        self._http_client = http_client if http_client else App().http_client()
        self._db = db if db else App().db()

    def exec(self):
        for coin in self._config.supported_coins():
            height = FetchBlockchainHeightUC(coin, config=self._config, http_client=self._http_client).exec()
            if height:
                self._db.update_blockchain_height(coin, self._config.cc_network(coin), height)
            else:
                log.warning(f'Can\'t fetch {coin.upper()} blockchain height from any source. Network connection issue?')
