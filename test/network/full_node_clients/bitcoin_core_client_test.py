from cypherpunkpay.common import *
from cypherpunkpay.bitcoin import Bip32
from cypherpunkpay.full_node_clients.bitcoin_core_client import BitcoinCoreClient
from cypherpunkpay.full_node_clients.json_rpc_client import JsonRpcError

from test.network.network_test_case import CypherpunkpayNetworkTestCase


class BitcoinCoreClientTest(CypherpunkpayNetworkTestCase):

    # Requires testnet bitcoind running on localhost with RPC server listening with default settings

    # CypherpunkPay development testnet wallet for testing getting address credits
    #
    # Mnemonic seed:
    # dial mango trade true sustain creek security wood cargo giggle robot noble
    #
    # Name:
    # cypherpunkpay-development-fetch-address-credits
    XPUB = 'vpub5YJSWL2hapFuX1Gz9jfSZuubEPPC6ncnhWCYo2g7ToWKAcxxgomLWh6NNEBo2ErebqPcFAmXY91FQFB977fA9eS4zV8WfabWTdiSz9QfGB3'
    UNSPENT_ADDRESS_0_0 = 'tb1q9gnjmsu52696ntv73g3qkn347rpu0hga7djsky'
    SPENT_ADDRESS_0_1 = 'tb1qcmxu8l7qqk2v7d0ef5t5q83gmu3w2e7mlxdkcw'
    UNSPENT_ADDRESS_0_20 = 'tb1qwqfmw0s5gjc8z57wp8s5afdjee4mm4zf5a65hr'
    UNSPENT_ADDRESS_0_101 = 'tb1quataw3fl68yjggykft7gwymg6hxn9x6qt42e7u'

    def test_get_height_success(self):
        client = BitcoinCoreClient('http://127.0.0.1:18332', rpc_user='bitcoin', rpc_password='secret', http_client=self.tor_http_client)
        height = client.get_height()
        self.assertGreater(height, 1_972_225)
        self.assertLess(height, 6_000_000)

    def test_get_height_failure(self):
        client = BitcoinCoreClient('http://127.0.0.1:18332', rpc_user='bitcoin', rpc_password='incorrect password', http_client=self.tor_http_client)
        with self.assertRaises(JsonRpcError):
            client.get_height()

    def test_create_wallet_idempotent(self):
        client = BitcoinCoreClient('http://127.0.0.1:18332', rpc_user='bitcoin', rpc_password='secret', http_client=self.tor_http_client)

        # New xpub
        xprv, xpub = Bip32.generate_testnet_p2wpkh_wallet()
        client.create_wallet_idempotent(xpub)

        # Existing xpub
        client.create_wallet_idempotent(xpub)

    def test_fetch_address_credits(self):
        client = BitcoinCoreClient('http://127.0.0.1:18332', rpc_user='bitcoin', rpc_password='secret', http_client=self.tor_http_client)

        timestamp_before_example_transactions = int(datetime.datetime(2021, 4, 1).timestamp())
        client.create_wallet_idempotent(BitcoinCoreClientTest.XPUB, rescan_since=timestamp_before_example_transactions)

        wallet_fingerprint = Bip32.wallet_fingerprint(BitcoinCoreClientTest.XPUB)
        example_height = 1972757

        # Single payment of 1 satoshi to the first address
        credits = client.get_address_credits(wallet_fingerprint, BitcoinCoreClientTest.UNSPENT_ADDRESS_0_0, example_height)
        total_credited = sum(map(lambda c: c.value(), credits.any()))
        self.assertEqual(Decimal('0.00000001'), total_credited)

        # Address received funds got spent - we still expect these received funds to be properly recognized
        credits = client.get_address_credits(wallet_fingerprint, BitcoinCoreClientTest.SPENT_ADDRESS_0_1, example_height)
        total_credited = sum(map(lambda c: c.value(), credits.any()))
        self.assertEqual(Decimal('0.00013007'), total_credited)

        # Multiple payments to the address
        credits = client.get_address_credits(wallet_fingerprint, BitcoinCoreClientTest.UNSPENT_ADDRESS_0_20, example_height)
        total_credited = sum(map(lambda c: c.value(), credits.any()))
        self.assertEqual(
            Decimal('0.00003738') + Decimal('0.00009351') + Decimal('0.00018651') + Decimal('0.00003731') + Decimal('0.00003731'),
            total_credited
        )

        # Big gap address (/0/101) is recognized
        credits = client.get_address_credits(wallet_fingerprint, BitcoinCoreClientTest.UNSPENT_ADDRESS_0_101, example_height)
        total_credited = sum(map(lambda c: c.value(), credits.any()))
        self.assertEqual(Decimal('0.00001869'), total_credited)
