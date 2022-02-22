from test.acceptance.acceptance_test_case import CypherpunkpayAcceptanceTestCase


class AdminStatsViewTest(CypherpunkpayAcceptanceTestCase):

    def test_get_admin_stats(self):
        self.login()
        res = self.webapp.get(f'/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/stats', status=200)
        self.assertInBody(res, 'Stats')
