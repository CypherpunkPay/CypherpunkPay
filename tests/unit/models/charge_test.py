from cypherpunkpay.globals import *

from cypherpunkpay.models.charge import Charge, ExampleCharge


# Actual charge related logic is in the use cases and so are the tests
# Here we just smoke test a few methods
class ChargeTest:

    def test_instantiates(self):
        charge = Charge(total=Decimal('100.97'), currency='USD', time_to_pay_ms=1000, time_to_complete_ms=10_000)

        assert charge.uid
        assert charge.created_at

        assert charge.total == Decimal('100.97')
        assert charge.currency == 'usd'

        assert charge.cc_received_total == 0
        assert charge.pay_status == 'unpaid'
        assert charge.status == 'draft'

    def test_charge_description(self):
        # Donations
        charge = ExampleCharge.create(beneficiary=None, what_for=None, merchant_order_id=None)
        assert charge.description == 'Donation'

        charge = ExampleCharge.create(beneficiary='WikiLeaks', what_for=None, merchant_order_id=None)
        assert charge.description == 'Donation to WikiLeaks'

        charge = ExampleCharge.create(beneficiary=None, what_for='Free Assange', merchant_order_id=None)
        assert charge.description == 'Donation to Free Assange'

        charge = ExampleCharge.create(beneficiary='WikiLeaks', what_for='Free Assange', merchant_order_id=None)
        assert charge.description == 'Donation to WikiLeaks, Free Assange'

        # Merchant
        charge = ExampleCharge.create(beneficiary=None, what_for=None, merchant_order_id='437')
        assert 'Order 437, charge ' in charge.description

        charge = ExampleCharge.create(beneficiary='Tesla', what_for=None, merchant_order_id='437')
        assert 'Tesla, order 437, charge ' in charge.description

        charge = ExampleCharge.create(beneficiary=None, what_for='Model S', merchant_order_id='437')
        assert 'Model S, charge ' in charge.description

        charge = ExampleCharge.create(beneficiary='Tesla', what_for='Model S', merchant_order_id='437')
        assert 'Tesla, Model S, charge ' in charge.description
