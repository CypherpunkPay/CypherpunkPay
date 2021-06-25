from cypherpunkpay.common import *
from cypherpunkpay.usecases.base_charge_uc import BaseChargeUC
from cypherpunkpay.usecases.invalid_params import InvalidParams
from cypherpunkpay.app import App
from cypherpunkpay.models.charge import Charge


class CancelChargeUC(BaseChargeUC):

    def __init__(self, charge: Charge, db=None):
        self.db = db if db else App().db()
        self.charge = charge

    def exec(self) -> Charge:
        status_before = self.charge.status
        self.charge.status = 'cancelled'
        self.charge.cancelled_at = utc_now()
        self.db.save(self.charge)
        log.info(f'Charge {self.charge.short_uid()} status {status_before} -> cancelled')
        return self.charge
