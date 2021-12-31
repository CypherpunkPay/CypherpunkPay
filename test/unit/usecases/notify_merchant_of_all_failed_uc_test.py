from decimal import Decimal

from cypherpunkpay.usecases.notify_merchant_of_all_failed_uc import NotifyMerchantOfAllFailedUC
from test.unit.config.example_config import ExampleConfig
from cypherpunkpay import utc_now
from cypherpunkpay.models.charge import ExampleCharge
from test.unit.db_test_case import CypherpunkpayDBTestCase
from cypherpunkpay.net.http_client.dummy_http_client import DummyHttpClient


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


class NotifyMerchantOfAllFailedUCTest(CypherpunkpayDBTestCase):

    def test_exec(self):
        # NOT ELIGIBLE FOR NOTIFICATION

        # awaiting
        ExampleCharge.db_create(self.db, total=Decimal('1'), currency='usd', status='awaiting', merchant_order_id='ord-1')
        # completed
        ExampleCharge.db_create(self.db, uid='1', total=Decimal('1234567890.12'), currency='usd', status='completed', merchant_order_id='ord-2')
        # missing merchant_order_id
        ExampleCharge.db_create(self.db, total=Decimal('4'), currency='usd', status='expired', merchant_order_id=None)
        # already notified
        charge = ExampleCharge.db_create(self.db, total=Decimal('5'), currency='usd', status='expired', merchant_order_id='ord-3')
        charge.merchant_callback_url_called_at = utc_now()
        self.db.save(charge)

        # ELIGIBLE FOR NOTIFICATION

        # expired
        ExampleCharge.db_create(self.db, total=Decimal('2'), currency='usd', status='expired', merchant_order_id='ord-10')
        # cancelled
        ExampleCharge.db_create(self.db, total=Decimal('3'), currency='usd', status='cancelled', merchant_order_id='ord-11')

        mock_http_client = MockHttpClient()
        NotifyMerchantOfAllFailedUC(db=self.db, config=ExampleConfig(), http_client=mock_http_client).exec()

        self.assertEqual(2, mock_http_client.counter)
