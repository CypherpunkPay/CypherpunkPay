import logging as log
from decimal import Decimal

from test.internet.cypherpunkpay.cypherpunkpay_network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.full_node_clients.json_rpc_client import JsonRpcClient, JsonRpcRequestError, JsonRpcAuthenticationError, JsonRpcCallError
from cypherpunkpay.lightning_node_clients.lnd_client import LndClient


class LndClientTest(CypherpunkpayNetworkTestCase):

    # Requires testnet lnd running on localhost with RPC server listening with default settings
    # TODO: publish development macaroon files so others can run the tests

    def test_success(self):
        macaroon = '0201036c6e640258030a1048e0f05f02ff3f5ff7a4046ba186016e1201301a160a0761646472657373120472656164120577726974651a170a08696e766f69636573120472656164120577726974651a0f0a076f6e636861696e120472656164000006208778b5873594d4033de9b6b945d56e5b09cb00bb6001208d4366e8b348bd6a5f'
        lnd_client = LndClient('https://127.0.0.1:8081', macaroon=macaroon)

        one_satoshi = Decimal(0.00000001)
        payment_request = lnd_client.addinvoice(one_satoshi)
        log.info(f'{payment_request}=payment_request')

    # def test_bad_url(self):
    #     json_rpc_client = JsonRpcClient('http://127.0.0.1:68332', user='bitcoin', passwd='secret')
    #     with self.assertRaises(JsonRpcRequestError):
    #         json_rpc_client.getblockcount()
    #
    # def test_bad_password(self):
    #     json_rpc_client = JsonRpcClient('http://127.0.0.1:18332', user='bitcoin', passwd='bad password')
    #     with self.assertRaises(JsonRpcAuthenticationError):
    #         json_rpc_client.getblockcount()
    #
    # def test_bad_method(self):
    #     json_rpc_client = JsonRpcClient('http://127.0.0.1:18332', user='bitcoin', passwd='secret')
    #     with self.assertRaises(JsonRpcCallError):
    #         json_rpc_client.non_existing_method()
    #
    # def test_bad_param(self):
    #     json_rpc_client = JsonRpcClient('http://127.0.0.1:18332', user='bitcoin', passwd='secret')
    #     with self.assertRaises(JsonRpcCallError):
    #         json_rpc_client.getblockhash(1_000_000_000)
