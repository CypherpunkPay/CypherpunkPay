from cypherpunkpay.common import *
from cypherpunkpay.app import App
from cypherpunkpay.full_node_clients.bitcoin_core_client import BitcoinCoreClient
from cypherpunkpay.full_node_clients.json_rpc_client import JsonRpcError
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.usecases.use_case import UseCase


class FetchAddressCreditsFromBitcoinFullNodeUC(UseCase):

    def __init__(self, address: str, wallet_fingerprint: str, current_height=None, http_client=None, config=None):
        self.address = address
        self.wallet_fingerprint = wallet_fingerprint
        self.current_height = current_height if current_height is not None else App().current_blockchain_height('btc')
        self.http_client = http_client if http_client else App().http_client()
        self.config = config if config else App().config()

    def exec(self) -> [AddressCredits, None]:
        try:
            return BitcoinCoreClient(
                self.config.btc_node_rpc_url(),
                self.config.btc_node_rpc_user(),
                self.config.btc_node_rpc_password(),
                self.http_client
            ).get_address_credits(self.wallet_fingerprint, self.address, self.current_height)
        except JsonRpcError:
            return None  # The exception has been logged upstream. The action will be retried. Safe to swallow.
