from test.acceptance.acceptance_test_case import CypherpunkpayAcceptanceTestCase


class RootViewTest(CypherpunkpayAcceptanceTestCase):

    def test_get_not_prefixed_root(self):
        res = self.webapp.get('/', status=302)
        self.assertTrue(res.location.endswith('/cypherpunkpay/'))

    def test_get_root(self):
        res = self.webapp.get('/cypherpunkpay/', status=302)
        self.assertTrue(res.location.endswith('/donations'))
