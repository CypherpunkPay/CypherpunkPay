from cypherpunkpay.common import *
from tests.network.network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.full_node_clients.json_rpc_client import JsonRpcClient, JsonRpcRequestError, JsonRpcAuthenticationError, JsonRpcCallError


class JsonRpcClientTest(CypherpunkpayNetworkTestCase):

    # Requires testnet bitcoind running on localhost with RPC server listening with default settings

    def test_success(self):
        json_rpc_client = JsonRpcClient('http://127.0.0.1:18332', user='bitcoin', passwd='secret', http_client=self.clear_http_client)

        result = json_rpc_client.getblockchaininfo()
        blocks = result.get('blocks')
        self.assertGreater(blocks, 1_972_225)

        result = json_rpc_client.getblockcount()
        height = result
        self.assertEqual(height, blocks)

        result = json_rpc_client.getblockhash(height)
        self.assertIsInstance(result, str)

        result = json_rpc_client.listwallets()
        self.assertIsInstance(result, List)

    def test_bad_url(self):
        json_rpc_client = JsonRpcClient('http://127.0.0.1:68332', user='bitcoin', passwd='secret', http_client=self.clear_http_client)
        with self.assertRaises(JsonRpcRequestError):
            json_rpc_client.getblockcount()

    def test_bad_password(self):
        json_rpc_client = JsonRpcClient('http://127.0.0.1:18332', user='bitcoin', passwd='bad password', http_client=self.clear_http_client)
        with self.assertRaises(JsonRpcAuthenticationError):
            json_rpc_client.getblockcount()

    def test_bad_method(self):
        json_rpc_client = JsonRpcClient('http://127.0.0.1:18332', user='bitcoin', passwd='secret', http_client=self.clear_http_client)
        with self.assertRaises(JsonRpcRequestError):
            json_rpc_client.non_existing_method()

    def test_bad_param(self):
        json_rpc_client = JsonRpcClient('http://127.0.0.1:18332', user='bitcoin', passwd='secret', http_client=self.clear_http_client)
        with self.assertRaises(JsonRpcCallError):
            json_rpc_client.getblockhash(1_000_000_000)
