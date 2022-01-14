import logging
from decimal import Decimal

from cypherpunkpay.models.charge import Charge, ExampleCharge
from test.unit.test_case import CypherpunkpayTestCase


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

    def test_charge_description(self):
        # Donations
        charge = ExampleCharge.create(beneficiary=None, what_for=None, merchant_order_id=None)
        self.assertEqual(charge.description, 'Donation')

        charge = ExampleCharge.create(beneficiary='WikiLeaks', what_for=None, merchant_order_id=None)
        self.assertEqual(charge.description, 'Donation to WikiLeaks')

        charge = ExampleCharge.create(beneficiary=None, what_for='Free Assange', merchant_order_id=None)
        self.assertEqual(charge.description, 'Donation to Free Assange')

        charge = ExampleCharge.create(beneficiary='WikiLeaks', what_for='Free Assange', merchant_order_id=None)
        self.assertEqual(charge.description, 'Donation to WikiLeaks, Free Assange')

        # Merchant
        charge = ExampleCharge.create(beneficiary=None, what_for=None, merchant_order_id='437')
        self.assertMatch('Order 437, charge ', charge.description)

        charge = ExampleCharge.create(beneficiary='Tesla', what_for=None, merchant_order_id='437')
        self.assertMatch('Tesla, order 437, charge ', charge.description)

        charge = ExampleCharge.create(beneficiary=None, what_for='Model S', merchant_order_id='437')
        self.assertMatch('Model S, charge ', charge.description)

        charge = ExampleCharge.create(beneficiary='Tesla', what_for='Model S', merchant_order_id='437')
        self.assertMatch('Tesla, Model S, charge ', charge.description)
