from test.acceptance.app_test_case import CypherpunkpayAppTestCase


class DonationsViewTest(CypherpunkpayAppTestCase):

    def test_get_donations(self):
        self.webapp.get('/cypherpunkpay/donations', status=200)
