from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from cypherpunkpay.net.tor_client.base_tor_circuits import BaseTorCircuits
from test.network.network_test_case import CypherpunkpayNetworkTestCase
from cypherpunkpay.tools.safe_uid import SafeUid


class OfficialTorCircuitsTest(CypherpunkpayNetworkTestCase):

    EXAMPLE_ONION_URL = 'https://www.facebookwkhpilnemxj7asaniu7vnjjbiltxjqhye3mhbshg7kx5tfyd.onion/'
    EXAMPLE_CLEAR_URL = 'https://www.facebook.com/'
    EXAMPLE_CLEAR_URL2 = 'https://ifconfig.me/'

    def test_connects_clearnet_through_tor(self):
        label = SafeUid.gen()
        session = self.official_tor.get_for(label)
        res = session.get('https://check.torproject.org')
        self.assertTrue('Congratulations.' in res.text)

    def test_connects_onion(self):
        label = SafeUid.gen()
        session = self.official_tor.get_for(label)
        res = session.get(self.EXAMPLE_ONION_URL)
        self.assertTrue('facebook' in res.text)

    def test_reuses_circuit_for_the_same_label(self):
        label = SafeUid.gen()

        session1 = self.official_tor.get_for(label)
        session2 = self.official_tor.get_for(label)

        session1_ip = self.get_ip(session1)
        session2_ip = self.get_ip(session2)

        self.assertEqual(session1, session2)
        self.assertEqual(session1_ip, session2_ip)

    def test_creates_new_circuit_for_each_label(self):
        label1 = SafeUid.gen()
        session1 = self.official_tor.get_for(label1)

        label2 = SafeUid.gen()
        session2 = self.official_tor.get_for(label2)

        session1_ip = self.get_ip(session1)
        session2_ip = self.get_ip(session2)

        self.assertNotEqual(session1, session2)
        self.assertNotEqual(session1_ip, session2_ip)

    def test_thread_safety_for_the_same_label(self):
        label = SafeUid.gen()

        with ThreadPoolExecutor() as executor:
            futures = []
            for i in range(8):
                future = executor.submit(lambda: self.official_tor.get_for(label).get(self.EXAMPLE_CLEAR_URL))
                futures.append(future)

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    self.fail(f'Failure to get future.result() for future: {future.__dict__}')

    def test_thread_safety_for_different_labels(self):
        with ThreadPoolExecutor() as executor:
            futures = []
            for i in range(3):
                future = executor.submit(lambda: self.official_tor.get_for(SafeUid.gen()).get(self.EXAMPLE_CLEAR_URL))
                futures.append(future)

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    self.fail(f'Failure to get future.result() for future: {future.__dict__}')

    def test_skip_tor_label_does_not_use_tor(self):
        session = self.official_tor.get_for(BaseTorCircuits.SKIP_TOR)
        ip_disabled_tor = self.get_ip(session)

        with requests.Session() as session2:
            ip_clear = self.get_ip(session2)

        self.assertEqual(ip_disabled_tor, ip_clear)

    # @unittest.skip("TODO: needs to somehow change the circuit / label / socks5 user:pass")
    # def test_mark_as_broken_resets_tor_circuit(self):
    #     label = SafeUid.gen()
    #
    #     session1 = self.official_tor.get_for(label)
    #     session1_ip = self.get_ip(session1)
    #
    #     # let's assume the circuit is broken
    #     self.official_tor.mark_as_broken(label)
    #
    #     session2 = self.official_tor.get_for(label)
    #     session2_ip = self.get_ip(session2)
    #
    #     self.assertNotEqual(session1, session2)
    #     self.assertNotEqual(session1_ip, session2_ip)

    @staticmethod
    def get_ip(session):
        # Alternative: https://ip.seeip.org/jsonip
        return session.get('https://api.myip.com/').json()['ip']

    @staticmethod
    def get_ip_alt(session):
        return session.get('https://ip.seeip.org/jsonip').json()['ip']
