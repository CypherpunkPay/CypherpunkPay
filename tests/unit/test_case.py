import pytest

from cypherpunkpay.globals import *


class CypherpunkpayTestCase:

    ONE_SATOSHI = Decimal('0.00000001')
    ONE_CENT = Decimal('0.01')

    EXAMPLE_PAYMENT_REQUEST_TESTNET = 'lntb20m1pvjluezhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqspp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfpp3x9et2e20v6pu37c5d9vax37wxq72un98kmzzhznpurw9sgl2v0nklu2g4d0keph5t7tj9tcqd8rexnd07ux4uv2cjvcqwaxgj7v4uwn5wmypjd5n69z2xm3xgksg28nwht7f6zspwp3f9t'

    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    @staticmethod
    def script_dir(python_script_path):
        return os.path.dirname(os.path.realpath(python_script_path))

    @staticmethod
    def examples_dir(python_script_path):
        return f"{CypherpunkpayTestCase.script_dir(python_script_path)}/test_data"

    # TODO: deprecated
    def assertEqual(self, expected, candidate):
        assert candidate == expected

    # TODO: deprecated
    def assertNotEqual(self, expected, candidate):
        assert candidate != expected

    # TODO: deprecated
    def assertIsNone(self, expr):
        assert expr is None

    # TODO: deprecated
    def assertIn(self, expected_content: str, s):
        assert expected_content in s

    # TODO: deprecated
    def assertNotIn(self, expected_content: str, s):
        assert not expected_content in s

    # TODO: deprecated
    def assertTrue(self, expr):
        assert expr

    # TODO: deprecated
    def assertFalse(self, expr):
        assert not expr

    # TODO: deprecated
    def assertIsNotNone(self, expr):
        assert expr is not None

    # TODO: deprecated
    def assertEmpty(self, expr, msg=None):
        assert not expr

    # TODO: deprecated
    def assertNotEmpty(self, expr, msg=None):
        assert expr

    # TODO: deprecated
    def assertMatch(self, expected_regex, expr, msg=None):
        import re
        assert re.match(expected_regex, expr)

    # TODO: deprecated
    def assertGreater(self, expr, than):
        assert expr > than

    # TODO: deprecated
    def assertLess(self, expr, than):
        assert expr < than

    def gen_tmp_file_path(self, suffix=None):
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(mode='w+b', prefix='cypherpunkpay-test-', suffix=suffix) as file:
            return file.name
