from cypherpunkpay.common import *

import pytest

from cypherpunkpay.bitcoin.electrum.constants import BitcoinTestnet
from test.network.network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.lightning_node_clients.lnd_client import LndClient, LightningException, UnknownInvoiceLightningException, InvalidMacaroonLightningException
from cypherpunkpay.bitcoin.electrum.lnaddr import lndecode
from test.unit.test_case import CypherpunkpayTestCase


class LndClientTest(CypherpunkpayNetworkTestCase):

    DEV_LND_URL = 'https://127.0.0.1:8081'
    DEV_LND_INVOICE_MACAROON = '0201036c6e640258030a100749d833cb20ba2b00af5ac46dcf70331201301a160a0761646472657373120472656164120577726974651a170a08696e766f69636573120472656164120577726974651a0f0a076f6e636861696e120472656164000006200d848586e393814cd8237db32d9e7192854dc05eba578b065a78dba6021af448'

    DEV_LND_INVALID_INVOICE_MACAROON = '0201036c6e640258030a1048e0f05f02ff3f5ff7a4046ba186016e1201301a160a0761646472657373120472656164120577726974651a170a08696e766f69636573120472656164120577726974651a0f0a076f6e636861696e120472656164000006208778b5873594d4033de9b6b945d56e5b09cb00bb6001208d4366e8b348bd6a5f'
    DEV_LND_MALFORMED_INVOICE_MACAROON = '02ae'
    DEV_LND_INVALID_PAYMENT_HASH = b'\xf1i\xf4\xc6\xe9\x9c\x97\xfaI\xfb"\xe8\xff\x0e\xc9\xf4\xbe\xdb\xc6\xc3:\x0f\xe3I.\x0b\xf1\xac$\xfd\xa9\x0e'
    DEV_LND_IRRELEVANT_PAYMENT_HASH = b'\xf1i\xf4\xc6\xe9\x9c\x97\xfaI\xfb"\xe8\xff\x0e\xc9\xf4\xbe\xdb\xc6\xc3:\x0f\xe3I.\x0b\xf1\xac$\xfd\xa9\x0e'

    # Requires testnet lnd running on localhost with REST API server listening with default settings
    # TODO: publish development macaroon files so others can run the tests

    def test_malformed_lnd_url(self):
        with pytest.raises(LightningException):
            LndClient('malformed url', invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client).addinvoice()

    def test_lnd_down(self):
        with pytest.raises(LightningException):
            LndClient('https://127.0.0.1:65535', invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client).addinvoice()

    def test_cant_be_http(self):
        with pytest.raises(LightningException):
            LndClient('http://127.0.0.1:8081', invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client).addinvoice()

    def test_malformed_invoice_macaroon(self):
        with pytest.raises(LightningException):
            LndClient(self.DEV_LND_URL, invoice_macaroon='0ea3', http_client=self.clear_http_client).addinvoice()

    def test_invalid_invoice_macaroon(self):
        with pytest.raises(InvalidMacaroonLightningException):
            LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVALID_INVOICE_MACAROON, http_client=self.clear_http_client).addinvoice()

    # addinvoice

    def test_too_big_amount(self):
        with pytest.raises(LightningException):
            lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
            lnd_client.addinvoice(Decimal('21_000_001'))

    def test_too_small_amount(self):
        with pytest.raises(LightningException):
            lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
            lnd_client.addinvoice(Decimal('-0.00000001'))

    def test_success_no_amount(self):
        lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
        payment_request_bech32 = lnd_client.addinvoice()
        payment_request = lndecode(payment_request_bech32, net=BitcoinTestnet)
        assert payment_request.get_amount_sat() is None

    def test_success_one_satoshi(self):
        lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
        payment_request_bech32 = lnd_client.addinvoice(total_btc=self.ONE_SATOSHI)
        payment_request = lndecode(payment_request_bech32, net=BitcoinTestnet)
        assert payment_request.get_amount_sat() == 1

    def test_success_with_memo(self):
        lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
        payment_request_bech32 = lnd_client.addinvoice(total_btc=0.06543210, memo='Ƀ')
        payment_request = lndecode(payment_request_bech32, net=BitcoinTestnet)
        assert payment_request.get_amount_sat() == 6543210
        assert payment_request.get_description() == 'Ƀ'

    def test_success_with_expiry(self):
        lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
        EXPIRY = 60*15
        payment_request_bech32 = lnd_client.addinvoice(expiry_seconds=EXPIRY)
        payment_request = lndecode(payment_request_bech32, net=BitcoinTestnet)
        assert payment_request.get_expiry() == EXPIRY

    # lookupinvoice

    def test_unknown_payment_hash(self):
        lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
        with pytest.raises(UnknownInvoiceLightningException):
            lnd_client.lookupinvoice(self.DEV_LND_INVALID_PAYMENT_HASH)

    def test_success_invoice_not_settled(self):
        lnd_client = LndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
        payment_request = lnd_client.addinvoice()
        valid_payment_hash = lndecode(payment_request, net=BitcoinTestnet).paymenthash
        ln_invoice = lnd_client.lookupinvoice(valid_payment_hash)
        assert not ln_invoice.is_settled
        assert ln_invoice.amt_paid_sat == 0

    def test_success_invoice_settled(self):
        class StubLndClient(LndClient):
            def _http_get(self, headers_d, lnd_node_url):
                response_text = Path(f"{CypherpunkpayTestCase.examples_dir(__file__)}/lnd_lookupinvoice_settled_2sats.json").read_text()
                return SimpleNamespace(text=response_text)

        lnd_client = StubLndClient(self.DEV_LND_URL, invoice_macaroon=self.DEV_LND_INVOICE_MACAROON, http_client=self.clear_http_client)
        ln_invoice = lnd_client.lookupinvoice(self.DEV_LND_IRRELEVANT_PAYMENT_HASH)

        assert ln_invoice.is_settled
        assert ln_invoice.amt_paid_sat == 2
