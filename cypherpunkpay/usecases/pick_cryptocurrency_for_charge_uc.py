from cypherpunkpay.common import *
from cypherpunkpay.usecases.base_charge_uc import BaseChargeUC
from cypherpunkpay.usecases.invalid_params import InvalidParams
from cypherpunkpay.app import App
from cypherpunkpay.models.charge import Charge


class PickCryptocurrencyForChargeUC(BaseChargeUC):

    BTC_PRECISION = 8
    XMR_PRECISION = 12

    def __init__(self, charge: Charge, cc_currency: str, config=None, db=None, price_tickers=None):
        self.config = config if config else App().config()
        self.db = db if db else App().db()
        self.price_tickers = price_tickers if price_tickers else App().price_tickers()
        self.charge = charge
        self.cc_currency = cc_currency

    def exec(self):
        self.validate_inputs()

        charge = self.charge

        charge.cc_currency = self.cc_currency
        charge.cc_price = self.price_tickers.price(charge.cc_currency, charge.currency)
        charge.cc_total = round(charge.total / charge.cc_price, self.BTC_PRECISION)

        cc_usd_price = self.price_tickers.usd_price(charge.cc_currency)
        charge.usd_total = round(charge.cc_total * cc_usd_price, 2)

        wallet_fingerprint, address_index, address = self.next_unused_address(self.cc_currency)
        charge.wallet_fingerprint = wallet_fingerprint
        charge.address_derivation_index = address_index
        charge.cc_address = address

        charge.advance_to_awaiting()

        self.db.save(charge)
        return charge

    def validate_inputs(self):
        errors = {}
        errors.update(self.validate_charge())
        errors.update(self.validate_cc_currency())
        if errors:
            raise InvalidParams(errors)

    def validate_charge(self) -> Dict[str, str]:
        if self.charge is None:
            return {'charge': f"Charge cannot be None"}
        if not self.charge.is_draft():
            return {'charge': f"Charge is not a draft, unexpected status={self.charge.status}"}
        return {}

    def validate_cc_currency(self) -> Dict[str, str]:
        if self.cc_currency not in self.config.supported_coins():
            return {'cc_currency': f"Unsupported coin '{self.cc_currency}'"}
        if self.cc_currency not in self.config.configured_coins():
            return {'cc_currency': f"No wallet configured for {self.config.cc_network(self.cc_currency)} {self.cc_currency}"}
        return {}
