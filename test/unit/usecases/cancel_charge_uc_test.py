from cypherpunkpay.models.charge import ExampleCharge
from cypherpunkpay.usecases.cancel_charge_uc import CancelChargeUC
from test.unit.db_test_case import CypherpunkpayDBTestCase


class CancelChargeUCTest(CypherpunkpayDBTestCase):

    def test_cancels_charge(self):
        charge = ExampleCharge.db_create(db=self.db)
        CancelChargeUC(charge=charge, db=self.db).exec()
        charge = self.db.reload(charge)
        self.assertEqual('cancelled', charge.status)
