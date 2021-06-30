import logging as log
from decimal import Decimal

from cypherpunkpay.bitcoin.electrum.constants import BitcoinTestnet
from test.internet.cypherpunkpay.cypherpunkpay_network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.full_node_clients.json_rpc_client import JsonRpcClient, JsonRpcRequestError, JsonRpcAuthenticationError, JsonRpcCallError
from cypherpunkpay.lightning_node_clients.lnd_client import LndClient, LightningException


class LndClientTest(CypherpunkpayNetworkTestCase):

    DEV_LND_URL = 'https://127.0.0.1:8081'
    DEV_LND_INVOICE_MACAROON = '0201036c6e640258030a1048e0f05f02ff3f5ff7a4046ba186016e1201301a160a0761646472657373120472656164120577726974651a170a08696e766f69636573120472656164120577726974651a0f0a076f6e636861696e120472656164000006208778b5873594d4033de9b6b945d56e5b09cb00bb6001208d4366e8b348bd6a5f'
    DEV_LND_INVALID_INVOICE_MACAROON = '02ae'
    ONE_SATOSHI = Decimal('0.00000001')

    # Requires testnet lnd running on localhost with REST API server listening with default settings
    # TODO: publish development macaroon files so others can run the tests

    def test_malformed_url(self):
        with self.assertRaises(LightningException):
            LndClient('malformed url', invoice_macaroon=self.DEV_LND_INVOICE_MACAROON).addinvoice()

    def test_lnd_down(self):
        with self.assertRaises(LightningException):
            LndClient('https://127.0.0.1:65535', invoice_macaroon=self.DEV_LND_INVOICE_MACAROON).addinvoice()

    def test_cant_be_http(self):
        with self.assertRaises(LightningException):
            LndClient('http://127.0.0.1:8081', invoice_macaroon=self.DEV_LND_INVOICE_MACAROON).addinvoice()

    def test_invalid_invoice_macaroon(self):
        with self.assertRaises(LightningException):
            LndClient(self.DEV_LND_URL, invoice_macaroon='0ea3').addinvoice()

    def test_too_big_amount(self):
        with self.assertRaises(LightningException):
            lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON)
            lnd_client.addinvoice(Decimal('21_000_001'))

    def test_too_small_amount(self):
        with self.assertRaises(LightningException):
            lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON)
            lnd_client.addinvoice(Decimal('-0.00000001'))

    def test_success_no_amount(self):
        lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON)
        payment_request = lnd_client.addinvoice()
        from cypherpunkpay.bitcoin.electrum.lnaddr import lndecode
        decoded = lndecode(payment_request, net=BitcoinTestnet)
        # decoded.amount
        print(decoded.__dict__)
        log.info(f'{payment_request}=payment_request')
