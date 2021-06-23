from decimal import Decimal

from cypherpunkpay.app import App
from test.acceptance.cypherpunkpay.cypherpunkpay_app_test_case import CypherpunkpayAppTestCase
from cypherpunkpay.models.dummy_store_order import DummyStoreOrder


class DummystoreViewsTest(CypherpunkpayAppTestCase):

    def test_get_dummystore_root(self):
        res = self.webapp.get('/cypherpunkpay/dummystore/', status=200)
        self.assertInBody(res, 'Demo Store')

    def test_post_cypherpunkpay_payment_completed__authorization_missing(self):
        res = self.webapp.post('/cypherpunkpay/dummystore/cypherpunkpay_payment_completed', params='{}', expect_errors=True)
        self.assertEqual(403, res.status_int)

    def test_post_cypherpunkpay_payment_completed__authorization_incorrect(self):
        incorrect_auth_header = {'Authorization': 'Bearer incorrectvaluehere'}
        res = self.webapp.post('/cypherpunkpay/dummystore/cypherpunkpay_payment_completed', headers=incorrect_auth_header, params='{}', expect_errors=True)
        self.assertEqual(403, res.status_int)

    def test_post_cypherpunkpay_payment_completed__merchant_order_id_missing(self):
        res = self.webapp.post('/cypherpunkpay/dummystore/cypherpunkpay_payment_completed', headers=self.correct_auth_header(), params='{}', expect_errors=False)
        self.assertEqual(200, res.status_int)

    def test_post_cypherpunkpay_payment_completed__body_is_not_json(self):
        order = DummyStoreOrder(uid='ord-1', item_id=0, total=10, currency='usd')
        App().db().insert(order)
        data_broken_json = '{ fsdfsd'
        res = self.webapp.post('/cypherpunkpay/dummystore/cypherpunkpay_payment_completed', headers=self.correct_auth_header(), params=data_broken_json, expect_errors=True)
        self.assertEqual(400, res.status_int)

    def test_post_cypherpunkpay_payment_completed__total_counterfeited(self):
        order = DummyStoreOrder(uid='ord-2', item_id=0, total=10, currency='usd')
        App().db().insert(order)
        data_total_counterfeited = """
        {
            "untrusted": {
                "merchant_order_id": "ord-2",
                "total": "0.01",
                "currency": "usd"
            },

            "status": "completed",
            "cc_currency": "btc",
            "cc_total": "0.000001"
        }
        """
        res = self.webapp.post('/cypherpunkpay/dummystore/cypherpunkpay_payment_completed', headers=self.correct_auth_header(), params=data_total_counterfeited, expect_errors=False)
        self.assertEqual(200, res.status_int)

    def test_post_cypherpunkpay_payment_completed__currency_counterfeited(self):
        order = DummyStoreOrder(uid='ord-3', item_id=0, total=10, currency='usd')
        App().db().insert(order)
        data_currency_counterfeited = """
        {
            "untrusted": {
                "merchant_order_id": "ord-3",
                "total": "10.00",
                "currency": "cny"
            },

            "status": "completed",
            "cc_currency": "btc",
            "cc_total": "0.000001"
        }
        """
        res = self.webapp.post('/cypherpunkpay/dummystore/cypherpunkpay_payment_completed', headers=self.correct_auth_header(), params=data_currency_counterfeited, expect_errors=False)
        self.assertEqual(200, res.status_int)

    def test_post_cypherpunkpay_payment_completed__ships_order(self):
        order = DummyStoreOrder(uid='ord-4', item_id=0, total=10, currency='USD')
        App().db().insert(order)
        data_correct = """
        {
            "untrusted": {
                "merchant_order_id": "ord-4",
                "total": "10",
                "currency": "usd"
            },

            "status": "completed",
            "cc_currency": "btc",
            "cc_total": "0.000197"
        }
        """
        res = self.webapp.post('/cypherpunkpay/dummystore/cypherpunkpay_payment_completed', headers=self.correct_auth_header(), params=data_correct, expect_errors=False)
        order = App().db().get_order_by_uid('ord-4')
        self.assertEqual(Decimal('0.000197'), order.cc_total)
        self.assertEqual('btc', order.cc_currency)
        self.assertEqual(200, res.status_int)

    def correct_auth_header(self) -> dict:
        return {'Authorization': 'Bearer nsrzukv53xjhmw4w5ituyk5cre'}
