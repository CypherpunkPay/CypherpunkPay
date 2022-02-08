from cypherpunkpay.common import *

import pytest

from cypherpunkpay.bitcoin.electrum.constants import BitcoinTestnet
from cypherpunkpay.ln.lightning_client import LightningException, UnknownInvoiceLightningException
from cypherpunkpay.ln.lightning_lightningd_client import LightningLightningdClient
from test.network.network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.bitcoin.electrum.lnaddr import lndecode


class LightningLightningdClientTest(CypherpunkpayNetworkTestCase):

    DEV_LIGHTNINGD_SOCKET_PATH = '/var/run/lightningd-testnet/lightning-rpc'
    DEV_LIGHTNINGD_INVALID_PAYMENT_HASH = b'\xf1i\xf4\xc6\xe9\x9c\x97\xfaI\xfb"\xe8\xff\x0e\xc9\xf4\xbe\xdb\xc6\xc3:\x0f\xe3I.\x0b\xf1\xac$\xfd\xa9\x0e'
    DEV_LIGHTNINGD_IRRELEVANT_PAYMENT_HASH = b'\xf1i\xf4\xc6\xe9\x9c\x97\xfaI\xfb"\xe8\xff\x0e\xc9\xf4\xbe\xdb\xc6\xc3:\x0f\xe3I.\x0b\xf1\xac$\xfd\xa9\x0e'

    # Requires testnet lightningd running on localhost with RPC socket at specific path and permissions

    def test_malformed_lightningd_socket_path(self):
        with pytest.raises(LightningException):
            LightningLightningdClient('malformed socket path').create_invoice()

    def test_incorrect_lightningd_socket_path(self):
        with pytest.raises(LightningException):
            LightningLightningdClient('/tmp/nonexisting').create_invoice()

    # ping

    def test_ping(self):
        lightningd_client = LightningLightningdClient(self.DEV_LIGHTNINGD_SOCKET_PATH)
        lightningd_client.ping()

    # create_invoice

    def test_zero_amount(self):
        with pytest.raises(LightningException):
            lightningd_client = LightningLightningdClient(self.DEV_LIGHTNINGD_SOCKET_PATH)
            lightningd_client.create_invoice(total_btc=0)

    def test_negative_amount(self):
        with pytest.raises(LightningException):
            lightningd_client = LightningLightningdClient(self.DEV_LIGHTNINGD_SOCKET_PATH)
            lightningd_client.create_invoice(total_btc=Decimal('-0.00000001'))

    def test_success_no_amount_no_description(self):
        lightningd_client = LightningLightningdClient(self.DEV_LIGHTNINGD_SOCKET_PATH)
        payment_request_bech32 = lightningd_client.create_invoice()
        payment_request = lndecode(payment_request_bech32, net=BitcoinTestnet)
        assert payment_request.get_amount_sat() is None
        assert payment_request.get_description() == ''

    def test_success_one_satoshi(self):
        lightningd_client = LightningLightningdClient(self.DEV_LIGHTNINGD_SOCKET_PATH)
        payment_request_bech32 = lightningd_client.create_invoice(total_btc=self.ONE_SATOSHI)
        payment_request = lndecode(payment_request_bech32, net=BitcoinTestnet)
        assert payment_request.get_amount_sat() == 1

    def test_success_big_amount(self):
        lightningd_client = LightningLightningdClient(self.DEV_LIGHTNINGD_SOCKET_PATH)
        payment_request_bech32 = lightningd_client.create_invoice(total_btc=Decimal('0.06543210'))
        payment_request = lndecode(payment_request_bech32, net=BitcoinTestnet)
        assert payment_request.get_amount_sat() == 6543210

    def test_success_with_description(self):
        lightningd_client = LightningLightningdClient(self.DEV_LIGHTNINGD_SOCKET_PATH)
        payment_request_bech32 = lightningd_client.create_invoice(memo='Ƀ')
        payment_request = lndecode(payment_request_bech32, net=BitcoinTestnet)
        assert payment_request.get_description() == 'Ƀ'

    def test_success_with_expiry(self):
        lightningd_client = LightningLightningdClient(self.DEV_LIGHTNINGD_SOCKET_PATH)
        EXPIRY = 60*15
        payment_request_bech32 = lightningd_client.create_invoice(expiry_seconds=EXPIRY)
        payment_request = lndecode(payment_request_bech32, net=BitcoinTestnet)
        assert payment_request.get_expiry() == EXPIRY

    # get_invoice

    def test_unknown_payment_hash(self):
        lightningd_client = LightningLightningdClient(self.DEV_LIGHTNINGD_SOCKET_PATH)
        with pytest.raises(UnknownInvoiceLightningException):
            lightningd_client.get_invoice(self.DEV_LIGHTNINGD_INVALID_PAYMENT_HASH)

    def test_success_invoice_not_settled(self):
        lightningd_client = LightningLightningdClient(self.DEV_LIGHTNINGD_SOCKET_PATH)
        payment_request = lightningd_client.create_invoice()
        log.warning(payment_request)
        valid_payment_hash = lndecode(payment_request, net=BitcoinTestnet).paymenthash
        log.warning(valid_payment_hash.hex())
        ln_invoice = lightningd_client.get_invoice(valid_payment_hash)
        assert not ln_invoice.is_settled
        assert ln_invoice.amt_paid_sat == 0

    def test_success_invoice_settled(self):
        class StubLightningLightningdClient(LightningLightningdClient):
            def _listinvoices(self, payment_hash):
                return {
                    'invoices': [{
                        'status': 'paid',
                        'amount_received_msat': 2000,
                    }]
                }

        lightningd_client = StubLightningLightningdClient(self.DEV_LIGHTNINGD_SOCKET_PATH)
        ln_invoice = lightningd_client.get_invoice(self.DEV_LIGHTNINGD_IRRELEVANT_PAYMENT_HASH)

        assert ln_invoice.is_settled
        assert ln_invoice.amt_paid_sat == 2
