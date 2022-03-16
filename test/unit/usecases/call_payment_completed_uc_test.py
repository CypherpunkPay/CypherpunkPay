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

        mock_http_client = MockHttpClient()
        CallPaymentCompletedUrlUC(charge=charge, db=self.db, config=ExampleConfig(), http_client=mock_http_client).exec()

        # Calls the right URL
        assert mock_http_client.url == 'http://127.0.0.1:6543/cypherpunkpay/dummystore/cypherpunkpay_payment_completed'

        # With tor privacy context
        assert mock_http_client.privacy_context == BaseTorCircuits.SHARED_CIRCUIT_ID

        # Has the right headers
        assert mock_http_client.headers.get('Authorization') == 'Bearer nsrzukv53xjhmw4w5ituyk5cre'
        assert mock_http_client.headers.get('Content-Type') == 'application/json'

        # Renders body correctly
        body = mock_http_client.body
        import json
        parsed_body = json.loads(body)
        assert parsed_body['untrusted']['merchant_order_id'] == 'ord-1'
        assert parsed_body['untrusted']['total'] == '1234567890.00000001'
        assert parsed_body['untrusted']['currency'] == 'usd'
        assert parsed_body['status'] == 'completed'
        assert parsed_body['cc_total'] == '1000.000000000001'
        assert parsed_body['cc_currency'] == 'btc'

        # Marks charge as notified
        charge_reloaded = self.db.get_charge_by_uid('1')
        assert charge_reloaded.merchant_callback_url_called_at is not None

    def test_exec_without_tor(self):
        charge = ExampleCharge.db_create(self.db, uid='1', total=Decimal('1234567890.00000001'), currency='usd', status='completed', merchant_order_id='ord-1', cc_total=Decimal('1000.000000000001'), cc_currency='btc')

        mock_http_client = MockHttpClient()

        config = ExampleConfig()
        config._dict['skip_tor_for_merchant_callbacks'] = 'true'

        CallPaymentCompletedUrlUC(charge=charge, db=self.db, config=config, http_client=mock_http_client).exec()

        # Calls the right URL
        assert 'http://127.0.0.1:6543/cypherpunkpay/dummystore/cypherpunkpay_payment_completed' == mock_http_client.url

        # With SKIP_TOR privacy context
        assert BaseTorCircuits.SKIP_TOR == mock_http_client.privacy_context
