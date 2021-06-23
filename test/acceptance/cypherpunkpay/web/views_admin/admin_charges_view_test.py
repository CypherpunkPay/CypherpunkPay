from test.acceptance.cypherpunkpay.cypherpunkpay_app_test_case import CypherpunkpayAppTestCase


class AdminChargesViewTest(CypherpunkpayAppTestCase):

    def test_get_admin_charges(self):
        self.login()
        res = self.webapp.get(f'/cypherpunkpay/admin/{self.admin_prefix()}/charges', status=200)
        self.assertInBody(res, 'Charges')
