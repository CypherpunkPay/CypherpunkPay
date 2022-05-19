from abc import ABC, abstractmethod

from cypherpunkpay.globals import *

from cypherpunkpay.models.ln_invoice_status import LnInvoiceStatus


class LightningException(Exception):
    pass


class UnauthorizedLightningException(LightningException):
    pass


class UnknownInvoiceLightningException(LightningException):
    pass


class LightningClient(ABC):

    # Test connects to node:
    @abstractmethod
    def ping(self) -> None:
        ...

    # Returns payment request string as defined in Bolt-11:
    # https://github.com/lightning/bolts/blob/master/11-payment-encoding.md
    # This string is suitable for the end-user.
    @abstractmethod
    def create_invoice(self, total_btc: [Decimal, None] = None, memo: str = None, expiry_seconds: [int, None] = None) -> str:
        ...

    # The r_hash must be of type bytes and length 32
    @abstractmethod
    def get_invoice(self, payment_hash: bytes) -> LnInvoiceStatus:
        ...

    @abstractmethod
    def name(self) -> str:
        ...

    def assert_payment_hash(self, r_hash: bytes):
        assert isinstance(r_hash, bytes)
        assert len(r_hash) == 32
