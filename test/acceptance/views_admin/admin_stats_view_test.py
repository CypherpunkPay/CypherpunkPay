from test.acceptance.app_test_case import CypherpunkpayAppTestCase


class AdminStatsViewTest(CypherpunkpayAppTestCase):

    def test_get_admin_stats(self):
        self.login()
        res = self.webapp.get(f'/cypherpunkpay/admin/{self.admin_prefix()}/stats', status=200)
        self.assertInBody(res, 'Stats')
