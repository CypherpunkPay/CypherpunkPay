from cypherpunkpay.usecases.base_charge_uc import BaseChargeUC
from cypherpunkpay.app import App
from cypherpunkpay.models.charge import Charge


class CancelChargeUC(BaseChargeUC):

    def __init__(self, charge: Charge, db=None):
        self.db = db if db else App().db()
        self.charge = charge

    def exec(self) -> Charge:
        self.charge.advance_to_cancelled()
        self.db.save(self.charge)
        return self.charge
