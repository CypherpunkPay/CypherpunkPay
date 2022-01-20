from decimal import Decimal
from typing import Dict

from cypherpunkpay.usecases.base_charge_uc import BaseChargeUC
from cypherpunkpay.usecases.invalid_params import InvalidParams
from cypherpunkpay.app import App
from cypherpunkpay.models.charge import Charge


class CreateChargeUC(BaseChargeUC):

    BTC_PRECISION = 8

    def __init__(self,
                 total: [str, Decimal],
                 currency: str,
                 merchant_order_id: str = None,
                 beneficiary=None,
                 what_for=None,
                 config=None,
                 db=None,
                 price_tickers=None,
                 qr_cache=None
                ):
        self.config = config if config else App().config()
        self.db = db if db else App().db()
        self.price_tickers = price_tickers if price_tickers else App().price_tickers()
        self.qr_cache = qr_cache if qr_cache is not None else App().qr_cache()

        self.total = total
        self.currency = currency
        self.merchant_order_id = merchant_order_id
        self.beneficiary = beneficiary
        self.what_for = what_for

        self.cc_currency = None
        self.wallet_fingerprint = None

        self.time_to_pay_ms = self.config.charge_payment_timeout_in_milliseconds()
        self.time_to_complete_ms = self.config.charge_completion_timeout_in_milliseconds()

        self.index = None
        self.address = None

    def exec(self) -> Charge:
        self.validate_inputs()

        # Draft charge (user will select cryptocurrency in the next step)
        charge = Charge(
            total=self.total,
            currency=self.currency,
            merchant_order_id=self.merchant_order_id,
            time_to_pay_ms=int(self.time_to_pay_ms),
            time_to_complete_ms=int(self.time_to_complete_ms),
            qr_cache=self.qr_cache
        )

        charge.beneficiary = self.beneficiary
        charge.what_for = self.what_for

        self.db.insert(charge)
        return charge

    def validate_inputs(self):
        errors = {}
        errors.update(self.validate_currency())
        errors.update(self.validate_total())
        if errors:
            raise InvalidParams(errors)

    def validate_currency(self) -> Dict[str, str]:
        currency = self.currency
        if currency == 'sats':
            currency = 'btc'  # locally for validation purposes only
        if currency in self.config.supported_fiats():
            return {}  # OK
        if currency in self.config.supported_coins():
            if currency in self.config.configured_coins():
                return {}  # OK
            else:
                return {'currency': f'No wallet configured for {self.config.cc_network(currency)} {currency}'}
        return {'currency': f'Unsupported currency'}

    def validate_total(self) -> Dict[str, str]:
        if self.total is None:
            return {'total': 'Amount cannot be empty'}
        if isinstance(self.total, str):
            try:
                self.total = Decimal(self.total)
            except Exception:
                return {'total': f'Invalid amount'}
        if isinstance(self.total, int):
            self.total = Decimal(self.total)
        if self.total <= 0:
            return {'total': 'Amount must be positive'}
        if self.currency in self.config.supported_fiats():
            if self.total < Decimal('0.01'):
                # Sub-penny fiat amounts disallowed
                return {'total': 'Amount too small'}
        if self.currency in self.config.supported_coins():
            if self.total < Decimal('0.00000001'):
                # Sub-satoshi for any cryptocurrency disallowed due to database precision of 8 decimal points
                return {'total': 'Amount too small'}
        if self.currency == 'sats':
            if self.total < 1:
                return {'total': 'Amount too small'}
            if self.total != int(self.total):
                return {'total': 'Amount in sats can\'t have decimals'}
        if self.total >= 92_233_720_369:
            # sqlite3 INTEGER is 8 bytes (including sign)
            # we use 8 digits (10**8) represent decimal part
            # that leaves us with
            # (2^63)/(10**8) = 92_233_720_369
            return {'total': 'Amount too large'}
        return {}
