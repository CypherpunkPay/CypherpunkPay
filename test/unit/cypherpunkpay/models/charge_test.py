from decimal import Decimal

from cypherpunkpay.models.charge import Charge
from test.unit.cypherpunkpay.cypherpunkpay_test_case import CypherpunkpayTestCase


# Actual charge related logic is in the use cases and so are the tests
# Here we just smoke test a few methods
class ChargeTest(CypherpunkpayTestCase):

    def test_instantiates(self):
        charge = Charge(total=Decimal('100.97'), currency='USD', time_to_pay_ms=1000, time_to_complete_ms=10_000)

        self.assertTrue(charge.uid)
        self.assertTrue(charge.created_at)

        self.assertEqual(charge.total, Decimal('100.97'))
        self.assertEqual(charge.currency, 'usd')

        self.assertEqual(charge.cc_received_total, 0)
        self.assertEqual(charge.pay_status, 'unpaid')
        self.assertEqual(charge.status, 'draft')
