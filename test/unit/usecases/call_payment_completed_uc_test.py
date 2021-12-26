from decimal import Decimal

from cypherpunkpay.net.tor_client.base_tor_circuits import BaseTorCircuits
from test.unit.config.example_config import ExampleConfig
from test.unit.db_test_case import CypherpunkpayDBTestCase
from cypherpunkpay.models.charge import ExampleCharge
from cypherpunkpay.net.http_client.dummy_http_client import DummyHttpClient
from cypherpunkpay.usecases.call_payment_completed_url_uc import CallPaymentCompletedUrlUC


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


class CallPaymentCompletedUrlUCTest(CypherpunkpayDBTestCase):

    def test_exec(self):
        charge = ExampleCharge.db_create(self.db, uid='1', total=Decimal('1234567890.00000001'), currency='usd', status='completed', merchant_order_id='ord-1', cc_total=Decimal('1000.000000000001'), cc_currency='btc')
        #ExampleCharge.db_create(self.db, uid='2', total=Decimal('1000.000000000001'), currency='xmr', status='completed', merchant_order_id='ord-2', cc_currency='xmr')

        mock_http_client = MockHttpClient()
        CallPaymentCompletedUrlUC(charge=charge, db=self.db, config=ExampleConfig(), http_client=mock_http_client).exec()

        # Calls the right URL
        self.assertEqual('http://127.0.0.1:6543/cypherpunkpay/dummystore/cypherpunkpay_payment_completed', mock_http_client.url)

        # With tor privacy context
        self.assertEqual(BaseTorCircuits.SHARED_CIRCUIT_ID, mock_http_client.privacy_context)

        # Has the right headers
        self.assertEqual('Bearer nsrzukv53xjhmw4w5ituyk5cre', mock_http_client.headers.get('Authorization'))
        self.assertEqual('application/json', mock_http_client.headers.get('Content-Type'))

        # Renders body correctly
        body = mock_http_client.body
        import json
        parsed_body = json.loads(body)
        self.assertTrue('untrusted' in parsed_body)
        self.assertTrue('status' in parsed_body)
        self.assertTrue('cc_total' in parsed_body)
        self.assertTrue('cc_currency' in parsed_body)
        self.assertTrue('"1234567890.00000001"' in body)
        self.assertTrue('"1000.000000000001"' in body)

        # Marks charge as notified
        charge_reloaded = self.db.get_charge_by_uid('1')
        self.assertIsNotNone(charge_reloaded.payment_completed_url_called_at)


    def test_exec_without_tor(self):
        charge = ExampleCharge.db_create(self.db, uid='1', total=Decimal('1234567890.00000001'), currency='usd', status='completed', merchant_order_id='ord-1', cc_total=Decimal('1000.000000000001'), cc_currency='btc')

        mock_http_client = MockHttpClient()

        config = ExampleConfig()
        config._dict['merchant_use_tor'] = 'false'  # disable tor for merchant request

        CallPaymentCompletedUrlUC(charge=charge, db=self.db, config=config, http_client=mock_http_client).exec()

        # Calls the right URL
        self.assertEqual('http://127.0.0.1:6543/cypherpunkpay/dummystore/cypherpunkpay_payment_completed', mock_http_client.url)

        # With local network privacy context
        self.assertEqual(BaseTorCircuits.LOCAL_NETWORK, mock_http_client.privacy_context)

        # Has the right headers
        self.assertEqual('Bearer nsrzukv53xjhmw4w5ituyk5cre', mock_http_client.headers.get('Authorization'))
        self.assertEqual('application/json', mock_http_client.headers.get('Content-Type'))

        # Renders body correctly
        body = mock_http_client.body
        import json
        parsed_body = json.loads(body)
        self.assertTrue('untrusted' in parsed_body)
        self.assertTrue('status' in parsed_body)
        self.assertTrue('cc_total' in parsed_body)
        self.assertTrue('cc_currency' in parsed_body)
        self.assertTrue('"1234567890.00000001"' in body)
        self.assertTrue('"1000.000000000001"' in body)

        # Marks charge as notified
        charge_reloaded = self.db.get_charge_by_uid('1')
        self.assertIsNotNone(charge_reloaded.payment_completed_url_called_at)
