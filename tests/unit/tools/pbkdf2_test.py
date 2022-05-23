from tests.unit.test_case import CypherpunkpayTestCase
from cypherpunkpay.tools.pbkdf2 import PBKDF2


class PBKDF2Test(CypherpunkpayTestCase):

    def test_pass(self):
        pass

    # A smoke test only! Implementation relies on built in pbkdf2 library
    def test_hash(self):
        h = PBKDF2.hash('password123')

        assert len(h) == (4 + 32 + 32) * 2

        EXPECTED_ITERATIONS = '000186a0'  # 100K iterations as unsigned 4 bytes
        assert h.startswith(EXPECTED_ITERATIONS)

    # If this starts failing then maybe the default 12 rounds is no longer enough
    def test_hash_speed(self):
        import time
        start = time.time()
        PBKDF2.hash('password123')
        end = time.time()
        assert end - start > 0.01  # seconds

    # Based on https://bcrypt-generator.com/
    def test_password_is_correct(self):
        assert PBKDF2.password_is_correct('', PBKDF2.hash(''))
        assert PBKDF2.password_is_correct('password123', PBKDF2.hash('password123'))
        assert PBKDF2.password_is_correct('QWERTYUIOPASDFGHJKLZXCVBNM!@#$%^&*(_+-={}|[];:,.<>', PBKDF2.hash('QWERTYUIOPASDFGHJKLZXCVBNM!@#$%^&*(_+-={}|[];:,.<>'))
