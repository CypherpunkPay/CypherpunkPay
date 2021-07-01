from decimal import Decimal

from cypherpunkpay.bitcoin.electrum.constants import BitcoinTestnet
from test.internet.cypherpunkpay.cypherpunkpay_network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.lightning_node_clients.lnd_client import LndClient, LightningException
from cypherpunkpay.bitcoin.electrum.lnaddr import lndecode


class LndClientTest(CypherpunkpayNetworkTestCase):

    DEV_LND_URL = 'https://127.0.0.1:8081'
    DEV_LND_INVOICE_MACAROON = '0201036c6e640258030a1048e0f05f02ff3f5ff7a4046ba186016e1201301a160a0761646472657373120472656164120577726974651a170a08696e766f69636573120472656164120577726974651a0f0a076f6e636861696e120472656164000006208778b5873594d4033de9b6b945d56e5b09cb00bb6001208d4366e8b348bd6a5f'
    DEV_LND_INVALID_INVOICE_MACAROON = '02ae'

    # Requires testnet lnd running on localhost with REST API server listening with default settings
    # TODO: publish development macaroon files so others can run the tests

    def test_malformed_lnd_url(self):
        with self.assertRaises(LightningException):
            LndClient('malformed url', invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client).addinvoice()

    def test_lnd_down(self):
        with self.assertRaises(LightningException):
            LndClient('https://127.0.0.1:65535', invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client).addinvoice()

    def test_cant_be_http(self):
        with self.assertRaises(LightningException):
            LndClient('http://127.0.0.1:8081', invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client).addinvoice()

    def test_invalid_invoice_macaroon(self):
        with self.assertRaises(LightningException):
            LndClient(self.DEV_LND_URL, invoice_macaroon='0ea3', http_client=self.clear_http_client).addinvoice()

    def test_too_big_amount(self):
        with self.assertRaises(LightningException):
            lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
            lnd_client.addinvoice(Decimal('21_000_001'))

    def test_too_small_amount(self):
        with self.assertRaises(LightningException):
            lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
            lnd_client.addinvoice(Decimal('-0.00000001'))

    def test_success_no_amount(self):
        lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
        payment_request_bech32 = lnd_client.addinvoice()
        payment_request = lndecode(payment_request_bech32, net=BitcoinTestnet)
        self.assertIsNone(payment_request.get_amount_sat())

    def test_success_one_satoshi(self):
        lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
        payment_request_bech32 = lnd_client.addinvoice(total_btc=self.ONE_SATOSHI)
        payment_request = lndecode(payment_request_bech32, net=BitcoinTestnet)
        self.assertEqual(1, payment_request.get_amount_sat())

    def test_success_with_memo(self):
        lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
        payment_request_bech32 = lnd_client.addinvoice(total_btc=0.06543210, memo='Ƀ')
        payment_request = lndecode(payment_request_bech32, net=BitcoinTestnet)
        self.assertEqual(6543210, payment_request.get_amount_sat())
        self.assertEqual('Ƀ', payment_request.get_description())

    def test_success_with_expiry(self):
        lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
        EXPIRY = 60*15
        payment_request_bech32 = lnd_client.addinvoice(expiry_seconds=EXPIRY)
        payment_request = lndecode(payment_request_bech32, net=BitcoinTestnet)
        self.assertEqual(EXPIRY, payment_request.get_expiry())
