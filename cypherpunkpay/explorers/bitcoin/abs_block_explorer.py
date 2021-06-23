from cypherpunkpay.common import *
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.net.http_client.base_http_client import BaseHttpClient
from cypherpunkpay.net.tor_client.base_tor_circuits import BaseTorCircuits


class AbsBlockExplorer(ABC):

    http_client: BaseHttpClient = None
    btc_network: str = None
    _use_tor: bool

    def __init__(self, http_client, btc_network='testnet', use_tor=True):
        self.http_client = http_client
        self.btc_network = btc_network
        self._use_tor = use_tor

    @abstractmethod
    def get_height(self) -> [int, None]:
        pass

    @abstractmethod
    def get_address_credits(self, address: str, current_height: int) -> [AddressCredits, None]:
        pass

    @abstractmethod
    def api_endpoint(self) -> str:
        pass

    def mainnet(self):
        return self.btc_network == 'mainnet'

    def use_tor(self):
        return self.use_tor

    def http_get_json_or_None_on_error(self, url: str, privacy_context: str) -> [Dict, None]:
        text = self.http_client.get_text_or_None_on_error(url, privacy_context)
        if text is not None:
            try:
                return json.loads(text)
            except JSONDecodeError as e:
                log.warning(f'Non JSON API response: {text}')

    def http_get_json_or_None_on_error_while_accepting_linkability(self, url: str) -> [Dict, None]:
        return self.http_get_json_or_None_on_error(url, privacy_context=BaseTorCircuits.SHARED_CIRCUIT_ID)
