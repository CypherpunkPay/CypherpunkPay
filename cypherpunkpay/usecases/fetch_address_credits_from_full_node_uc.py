from cypherpunkpay.app import App
from cypherpunkpay.common import *
from cypherpunkpay.exceptions import UnsupportedCoin
from cypherpunkpay.full_node_clients.bitcoin_core_client import BitcoinCoreClient
from cypherpunkpay.full_node_clients.json_rpc_client import JsonRpcError
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.usecases import UseCase


class FetchAddressCreditsFromFullNodeUC(UseCase):

    def __init__(self, cc_currency: str, address: str, wallet_fingerprint: str, current_height=None, http_client=None, config=None):
        self.cc_currency = cc_currency
        self.address = address
        self.wallet_fingerprint = wallet_fingerprint
        self.current_height = current_height if current_height is not None else App().current_blockchain_height('btc')
        self.http_client = http_client if http_client else App().http_client()
        self.config = config if config else App().config()

    def exec(self) -> [AddressCredits, None]:
        if self.cc_currency == 'btc':
            try:
                return BitcoinCoreClient(
                    self.config.btc_node_rpc_url(),
                    self.config.btc_node_rpc_user(),
                    self.config.btc_node_rpc_password(),
                    self.http_client
                ).get_address_credits(self.wallet_fingerprint, self.address, self.current_height)
            except JsonRpcError:
                return None  # The exception has been logged upstream. The action will be retried. Safe to swallow.
        if self.cc_currency == 'xmr':
            return AddressCredits([], 0)
        raise UnsupportedCoin(self.cc_currency)
