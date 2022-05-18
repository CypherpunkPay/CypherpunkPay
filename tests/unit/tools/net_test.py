from cypherpunkpay.tools.net import is_local_network, get_host_or_ip
from cypherpunkpay.tools.safe_uid import SafeUid

from tests.unit.test_case import CypherpunkpayTestCase


class NetTest(CypherpunkpayTestCase):

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

    def test_get_host_or_ip(self):
        assert get_host_or_ip('http://localhost') == 'localhost'
        assert get_host_or_ip('https://www.bitcoin.org:443') == 'www.bitcoin.org'
        assert get_host_or_ip('https://185.220.102.250/api/v1/tx/fewrwerw') == '185.220.102.250'
