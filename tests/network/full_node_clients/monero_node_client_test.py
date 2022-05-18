from cypherpunkpay.globals import *
from cypherpunkpay.full_node_clients.json_rpc_client import JsonRpcError
from cypherpunkpay.full_node_clients.monero_node_client import MoneroNodeClient

from tests.network.network_test_case import CypherpunkpayNetworkTestCase


class MoneroNodeClientTest(CypherpunkpayNetworkTestCase):

    # Requires stagenet monero open node http://stagenet.melo.tools:38081 running

    # CypherpunkPay development stagenet wallet for testing getting address credits
    #
    # Mnemonic seed:
    # TODO
    #
    # XPUB = 'vpub5YJSWL2hapFuX1Gz9jfSZuubEPPC6ncnhWCYo2g7ToWKAcxxgomLWh6NNEBo2ErebqPcFAmXY91FQFB977fA9eS4zV8WfabWTdiSz9QfGB3'
    # UNSPENT_ADDRESS_0_0 = 'tb1q9gnjmsu52696ntv73g3qkn347rpu0hga7djsky'
    # SPENT_ADDRESS_0_1 = 'tb1qcmxu8l7qqk2v7d0ef5t5q83gmu3w2e7mlxdkcw'
    # UNSPENT_ADDRESS_0_20 = 'tb1qwqfmw0s5gjc8z57wp8s5afdjee4mm4zf5a65hr'
    # UNSPENT_ADDRESS_0_101 = 'tb1quataw3fl68yjggykft7gwymg6hxn9x6qt42e7u'

    def test_get_height_success(self):
        client = MoneroNodeClient('http://stagenet.melo.tools:38081', http_client=self.tor_http_client)
        height = client.get_height()
        assert height > 1_061_100  # the moment tests were written
        assert height < 6_000_000  # arbitrary reasonable max height for the sake of tests

    def test_get_height_failure_bad_path(self):
        client = MoneroNodeClient('http://stagenet.melo.tools:38081/badpath', http_client=self.tor_http_client)
        with self.assertRaises(JsonRpcError):
             client.get_height()

    # def test_fetch_address_credits(self):
    #     client = BitcoinCoreClient('http://127.0.0.1:18332', rpc_user='bitcoin', rpc_password='secret', http_client=self.tor_http_client)
    #
    #     timestamp_before_example_transactions = int(datetime.datetime(2021, 4, 1).timestamp())
    #     client.create_wallet_idempotent(BitcoinCoreClientTest.XPUB, rescan_since=timestamp_before_example_transactions)
    #
    #     wallet_fingerprint = Bip32.wallet_fingerprint(BitcoinCoreClientTest.XPUB)
    #     example_height = 1972757
    #
    #     # Single payment of 1 satoshi to the first address
    #     credits = client.get_address_credits(wallet_fingerprint, BitcoinCoreClientTest.UNSPENT_ADDRESS_0_0, example_height)
    #     total_credited = sum(map(lambda c: c.value(), credits.all()))
    #     self.assertEqual(Decimal('0.00000001'), total_credited)
    #
    #     # Address received funds got spent - we still expect these received funds to be properly recognized
    #     credits = client.get_address_credits(wallet_fingerprint, BitcoinCoreClientTest.SPENT_ADDRESS_0_1, example_height)
    #     total_credited = sum(map(lambda c: c.value(), credits.all()))
    #     self.assertEqual(Decimal('0.00013007'), total_credited)
    #
    #     # Multiple payments to the address
    #     credits = client.get_address_credits(wallet_fingerprint, BitcoinCoreClientTest.UNSPENT_ADDRESS_0_20, example_height)
    #     total_credited = sum(map(lambda c: c.value(), credits.all()))
    #     self.assertEqual(
    #         Decimal('0.00003738') + Decimal('0.00009351') + Decimal('0.00018651') + Decimal('0.00003731') + Decimal('0.00003731'),
    #         total_credited
    #     )
    #
    #     # Big gap address (/0/101) is recognized
    #     credits = client.get_address_credits(wallet_fingerprint, BitcoinCoreClientTest.UNSPENT_ADDRESS_0_101, example_height)
    #     total_credited = sum(map(lambda c: c.value(), credits.all()))
    #     self.assertEqual(Decimal('0.00001869'), total_credited)
