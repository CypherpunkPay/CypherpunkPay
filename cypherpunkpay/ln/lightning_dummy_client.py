from cypherpunkpay.globals import *

from cypherpunkpay.models.ln_invoice_status import LnInvoiceStatus
from cypherpunkpay.ln.lightning_client import LightningClient


# Dummy implementations of abstract classes are used for testing
class LightningDummyClient(LightningClient):

    def ping(self) -> None:
        pass

    def create_invoice(self, total_btc: [Decimal, None] = None, memo: str = None, expiry_seconds: [int, None] = None) -> str:
        pass

    def get_invoice(self, payment_hash: bytes) -> LnInvoiceStatus:
        return LnInvoiceStatus()

    def name(self) -> str:
        return self.__class__.__name__
