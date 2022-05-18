from cypherpunkpay.tools.safe_uid import SafeUid

from tests.unit.test_case import CypherpunkpayTestCase


class SafeUidTest(CypherpunkpayTestCase):

    def test_safe_uid(self):
        SafeUid.gen()
