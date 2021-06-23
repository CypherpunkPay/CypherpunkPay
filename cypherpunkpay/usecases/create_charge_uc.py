from decimal import Decimal
from typing import Dict

from cypherpunkpay.usecases.base_charge_uc import BaseChargeUC
from cypherpunkpay.usecases.invalid_params import InvalidParams
from cypherpunkpay.app import App
from cypherpunkpay.models.charge import Charge


class CreateChargeUC(BaseChargeUC):

    BTC_PRECISION = 8

    def __init__(self, total: [str, Decimal], currency: str, merchant_order_id: str = None, config=None, db=None, price_tickers=None, qr_cache=None):
        self.config = config if config else App().config()
        self.db = db if db else App().db()
        self.price_tickers = price_tickers if price_tickers else App().price_tickers()
        self.qr_cache = qr_cache if qr_cache is not None else App().qr_cache()

        self.total = total
        self.currency = currency
        self.merchant_order_id = merchant_order_id

        self.cc_currency = None
        self.wallet_fingerprint = None

        self.time_to_pay_ms = self.config.charge_payment_timeout_in_milliseconds()
        self.time_to_complete_ms = self.config.charge_completion_timeout_in_milliseconds()

        self.index = None
        self.address = None

    def exec(self) -> Charge:
        self.validate_inputs()

        if self.currency in self.config.supported_fiats():
            # draft charge (user will select cryptocurrency in the next step)
            charge = Charge(
                total=self.total,
                currency=self.currency,
                merchant_order_id=self.merchant_order_id,
                time_to_pay_ms=int(self.time_to_pay_ms),
                time_to_complete_ms=int(self.time_to_complete_ms),
                qr_cache=self.qr_cache
            )
        else:
            # ready charge (payment total specified in cryptocurrency)
            charge = Charge(
                total=self.total,
                currency=self.currency,
                merchant_order_id=self.merchant_order_id,
                time_to_pay_ms=int(self.time_to_pay_ms),
                time_to_complete_ms=int(self.time_to_complete_ms),
                qr_cache=self.qr_cache
            )
            wallet_fingerprint, address_index, address = self.next_unused_address(self.currency)
            charge.cc_total = self.total
            charge.cc_currency = self.currency
            cc_usd_price = self.price_tickers.usd_price(charge.cc_currency)
            charge.usd_total = round(charge.cc_total * cc_usd_price, 2)
            charge.wallet_fingerprint = wallet_fingerprint
            charge.address_derivation_index = address_index
            charge.cc_address = address
            charge.advance_to_awaiting()

        self.db.insert(charge)
        return charge

    def validate_inputs(self):
        errors = {}
        errors.update(self.validate_currency())
        errors.update(self.validate_total())
        if errors:
            raise InvalidParams(errors)

    def validate_currency(self) -> Dict[str, str]:
        if self.currency in self.config.supported_fiats():
            return {}  # OK
        if self.currency in self.config.supported_coins():
            if self.currency in self.config.configured_coins():
                return {}  # OK
            else:
                return {'currency': f"No wallet configured for {self.config.cc_network(self.currency)} {self.currency}"}
        return {'currency': f"Unsupported currency"}

    def validate_total(self) -> Dict[str, str]:
        if self.total is None:
            return {'total': "Amount cannot be empty"}
        if isinstance(self.total, str):
            try:
                self.total = Decimal(self.total)
            except Exception:
                return {'total': f"Invalid amount"}
        if isinstance(self.total, int):
            self.total = Decimal(self.total)
        if self.total <= 0:
            return {'total': "Amount must be positive"}
        if self.total >= 92_233_720_369:
            # sqlite3 INTEGER is 8 bytes (including sign)
            # we use 8 digits (10**8) represent decimal part
            # that leaves us with
            # (2^63)/(10**8) = 92_233_720_369
            return {'total': "Amount too large"}
        return {}
