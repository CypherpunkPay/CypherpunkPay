from test.acceptance.acceptance_test_case import CypherpunkpayAcceptanceTestCase


class DonationsViewTest(CypherpunkpayAcceptanceTestCase):

    def test_get_donations(self):
        self.webapp.get('/cypherpunkpay/donations', status=200)
