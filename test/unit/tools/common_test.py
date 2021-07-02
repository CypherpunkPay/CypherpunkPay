from cypherpunkpay.common import *
from cypherpunkpay.tools.safe_uid import SafeUid

from test.unit.test_case import CypherpunkpayTestCase


class CommonTest(CypherpunkpayTestCase):

    def test_utc_now(self):
        self.assertEqual('UTC', utc_now().tzname())

    def test_utc_ago(self):
        min_ago_17 = utc_now() - datetime.timedelta(minutes=17)
        min_ago_18 = utc_ago(minutes=18)
        min_ago_19 = utc_now() - datetime.timedelta(minutes=19)
        self.assertLess(min_ago_18, min_ago_17)
        self.assertLess(min_ago_19, min_ago_18)

    def test_safe_ud(self):
        SafeUid.gen()

    def test_is_local_network(self):
        self.assertTrue(is_local_network('http://localhost/test'))
        self.assertTrue(is_local_network('http://localhost:8080/test'))

        self.assertTrue(is_local_network('http://127.0.0.1'))
        self.assertTrue(is_local_network('http://127.0.0.1:8080/test'))
        self.assertTrue(is_local_network('http://192.168.0.1/'))

        self.assertFalse(is_local_network('http://google.com'))
        self.assertFalse(is_local_network('http://mempoolhqx4isw62xs7abwphsq7ldayuidyx2v2oethdhhj6mlo2r6ad.onion'))
        self.assertFalse(is_local_network('http://google.com/localhost'))

    def test_get_domain_or_ip(self):
        self.assertEqual('localhost', get_domain_or_ip('http://localhost'))
        self.assertEqual('www.bitcoin.org', get_domain_or_ip('https://www.bitcoin.org:443'))
        self.assertEqual('185.220.102.250', get_domain_or_ip('https://185.220.102.250/api/v1/tx/fewrwerw'))
