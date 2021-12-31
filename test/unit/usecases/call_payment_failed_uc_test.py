from decimal import Decimal

from cypherpunkpay.net.tor_client.base_tor_circuits import BaseTorCircuits
from cypherpunkpay.usecases.call_payment_failed_url_uc import CallPaymentFailedUrlUC
from test.unit.config.example_config import ExampleConfig
from test.unit.db_test_case import CypherpunkpayDBTestCase
from cypherpunkpay.models.charge import ExampleCharge
from cypherpunkpay.net.http_client.dummy_http_client import DummyHttpClient


class StubResponse(object):
    @property
    def ok(self): return True
    @property
    def is_redirect(self): return False
    @property
    def status_code(self): return 200


class MockHttpClient(DummyHttpClient):

    url: str = None
    privacy_context: str = None
    headers: dict = None
    body: str = None

    def post(self, url, privacy_context, headers: dict = None, body: str = None, set_tor_browser_headers: bool = True, verify=None):
        self.url = url
        self.privacy_context = privacy_context
        self.headers = headers
        self.body = body
        return StubResponse()


class CallPaymentFailedUrlUCTest(CypherpunkpayDBTestCase):

    def test_exec__charge_cancelled(self):
        charge = ExampleCharge.db_create(self.db, uid='1', total=Decimal('9999.99'), currency='eur', status='cancelled', merchant_order_id='ord-1', cc_total=Decimal('0.000000000001'), cc_currency='xmr')

        mock_http_client = MockHttpClient()

        config = ExampleConfig()
        config._dict['payment_failed_notification_url'] = 'http://127.0.0.1:6543/cypherpunkpay/dummystore/cypherpunkpay_payment_failed'

        CallPaymentFailedUrlUC(charge=charge, db=self.db, config=config, http_client=mock_http_client).exec()

        # Calls the right URL
        self.assertEqual('http://127.0.0.1:6543/cypherpunkpay/dummystore/cypherpunkpay_payment_failed', mock_http_client.url)

        # With tor privacy context
        self.assertEqual(BaseTorCircuits.SHARED_CIRCUIT_ID, mock_http_client.privacy_context)

        # Has the right headers
        self.assertEqual('Bearer nsrzukv53xjhmw4w5ituyk5cre', mock_http_client.headers.get('Authorization'))
        self.assertEqual('application/json', mock_http_client.headers.get('Content-Type'))

        # Renders body correctly
        body = mock_http_client.body
        import json
        parsed_body = json.loads(body)
        self.assertEqual(parsed_body['untrusted']['merchant_order_id'], 'ord-1')
        self.assertEqual(parsed_body['untrusted']['total'], '9999.99')
        self.assertEqual(parsed_body['untrusted']['currency'], 'eur')
        self.assertEqual(parsed_body['status'], 'cancelled')

        # Marks charge as notified
        charge_reloaded = self.db.get_charge_by_uid('1')
        self.assertIsNotNone(charge_reloaded.merchant_callback_url_called_at)

    def test_exec__charge_expired(self):
        charge = ExampleCharge.db_create(self.db, uid='1', total=Decimal('9999.99'), currency='eur', status='expired', merchant_order_id='ord-1', cc_total=Decimal('0.000000000001'), cc_currency='xmr')

        mock_http_client = MockHttpClient()

        config = ExampleConfig()
        config._dict['payment_failed_notification_url'] = 'http://127.0.0.1:6543/cypherpunkpay/dummystore/cypherpunkpay_payment_failed'

        CallPaymentFailedUrlUC(charge=charge, db=self.db, config=config, http_client=mock_http_client).exec()

        # Calls the right URL
        self.assertEqual('http://127.0.0.1:6543/cypherpunkpay/dummystore/cypherpunkpay_payment_failed', mock_http_client.url)

        # With tor privacy context
        self.assertEqual(BaseTorCircuits.SHARED_CIRCUIT_ID, mock_http_client.privacy_context)

        # Has the right headers
        self.assertEqual('Bearer nsrzukv53xjhmw4w5ituyk5cre', mock_http_client.headers.get('Authorization'))
        self.assertEqual('application/json', mock_http_client.headers.get('Content-Type'))

        # Renders body correctly
        body = mock_http_client.body
        import json
        parsed_body = json.loads(body)
        self.assertEqual(parsed_body['untrusted']['merchant_order_id'], 'ord-1')
        self.assertEqual(parsed_body['untrusted']['total'], '9999.99')
        self.assertEqual(parsed_body['untrusted']['currency'], 'eur')
        self.assertEqual(parsed_body['status'], 'expired')

        # Marks charge as notified
        charge_reloaded = self.db.get_charge_by_uid('1')
        self.assertIsNotNone(charge_reloaded.merchant_callback_url_called_at)
