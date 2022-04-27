from tests.acceptance.acceptance_test_case import CypherpunkpayAcceptanceTestCase


class AdminChargesViewTest(CypherpunkpayAcceptanceTestCase):

    def test_get_admin_charges(self):
        self.login()
        res = self.webapp.get(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/charges', status=200)
        self.assertInBody(res, 'Charges')
