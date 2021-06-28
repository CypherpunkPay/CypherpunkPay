from decimal import Decimal

from test.unit.cypherpunkpay.app.example_config import ExampleConfig
from cypherpunkpay import utc_now, Config
from cypherpunkpay.models.charge import Charge, ExampleCharge
from test.unit.cypherpunkpay.cypherpunkpay_db_test_case import CypherpunkpayDBTestCase
from cypherpunkpay.net.http_client.dummy_http_client import DummyHttpClient
from cypherpunkpay.usecases.notify_merchant_of_all_completions_uc import NotifyMerchantOfAllCompletionsUC


class MockHttpClient(DummyHttpClient):

    class Response(object):
        @property
        def ok(self): return True
        @property
        def is_redirect(self): return False
        @property
        def status_code(self): return 200

    counter: int = 0

    def post(self, url, privacy_context, headers: dict = None, body: dict = None, set_tor_browser_headers: bool = True, verify=None):
        self.counter += 1
        return MockHttpClient.Response()


class NotifyMerchantOfAllCompletionsUCTest(CypherpunkpayDBTestCase):

    def test_exec(self):
        # NOT ELIGIBLE FOR NOTIFICATION

        # awaiting
        ExampleCharge.db_create(self.db, total=Decimal('1'), currency='usd', status='awaiting', merchant_order_id='a')
        # expired
        ExampleCharge.db_create(self.db, total=Decimal('2'), currency='usd', status='expired', merchant_order_id='b')
        # cancelled
        ExampleCharge.db_create(self.db, total=Decimal('3'), currency='usd', status='cancelled', merchant_order_id='c')
        # missing merchant_order_id
        ExampleCharge.db_create(self.db, total=Decimal('4'), currency='usd', status='completed', merchant_order_id=None)
        # already notified
        charge = ExampleCharge.db_create(self.db, total=Decimal('5'), currency='usd', status='completed', merchant_order_id='d', )
        charge.payment_completed_url_called_at = utc_now()
        self.db.save(charge)

        # ELIGIBLE FOR NOTIFICATION

        ExampleCharge.db_create(self.db, uid='1', total=Decimal('1234567890.12'), currency='usd', status='completed', merchant_order_id='ord-1')                            # <-- to be notified
        ExampleCharge.db_create(self.db, uid='2', total=Decimal('1000.000000000001'), currency='xmr', status='completed', merchant_order_id='ord-2', cc_currency='xmr')     # <-- to be notified

        mock_http_client = MockHttpClient()
        NotifyMerchantOfAllCompletionsUC(db=self.db, config=ExampleConfig(), http_client=mock_http_client).exec()

        self.assertEqual(2, mock_http_client.counter)
