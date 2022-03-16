from cypherpunkpay.common import *
from cypherpunkpay.tools.safe_uid import SafeUid

from test.unit.test_case import CypherpunkpayTestCase


class CommonTest(CypherpunkpayTestCase):

    def test_utc_now(self):
        assert utc_now().tzname() == 'UTC'

    def test_utc_ago(self):
        min_ago_17 = utc_now() - datetime.timedelta(minutes=17)
        min_ago_18 = utc_ago(minutes=18)
        min_ago_19 = utc_now() - datetime.timedelta(minutes=19)
        assert min_ago_18 < min_ago_17
        assert min_ago_18 < min_ago_17
        assert min_ago_19 < min_ago_18

    def test_safe_ud(self):
        SafeUid.gen()

    def test_is_local_network(self):
        assert is_local_network('http://localhost/test')
        assert is_local_network('http://localhost:8080/test')

        assert is_local_network('http://127.0.0.1')
        assert is_local_network('http://127.0.0.1:8080/test')
        assert is_local_network('http://192.168.0.1/')

        assert not is_local_network('http://google.com')
        assert not is_local_network('http://mempoolhqx4isw62xs7abwphsq7ldayuidyx2v2oethdhhj6mlo2r6ad.onion')
        assert not is_local_network('http://google.com/localhost')

    def test_get_domain_or_ip(self):
        assert get_domain_or_ip('http://localhost') == 'localhost'
        assert get_domain_or_ip('https://www.bitcoin.org:443') == 'www.bitcoin.org'
        assert get_domain_or_ip('https://185.220.102.250/api/v1/tx/fewrwerw') == '185.220.102.250'
