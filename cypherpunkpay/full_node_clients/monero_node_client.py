from cypherpunkpay.common import *
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.models.credit import Credit
from cypherpunkpay.net.http_client.base_http_client import BaseHttpClient
from cypherpunkpay.full_node_clients.json_rpc_client import JsonRpcClient


class MoneroNodeClient(object):

    _json_rpc_client: JsonRpcClient = None

    def __init__(self, url: str, rpc_user: str = '', rpc_password: str = '', http_client: BaseHttpClient = None):
        self._json_rpc_client = JsonRpcClient(url, user=rpc_user, passwd=rpc_password, http_client=http_client, path='/json_rpc')

    def get_height(self) -> int:
        return self._json_rpc_client.get_block_count()['count'] - 1  # height starts from 0 so it is smaller by one than the number of blocks
