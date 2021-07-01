import os
from decimal import Decimal
from tempfile import NamedTemporaryFile
from unittest.case import TestCase


class CypherpunkpayTestCase(TestCase):

    ONE_SATOSHI = Decimal('0.00000001')

    @staticmethod
    def script_dir(python_script_path):
        return os.path.dirname(os.path.realpath(python_script_path))

    @staticmethod
    def examples_dir(python_script_path):
        return f"{CypherpunkpayTestCase.script_dir(python_script_path)}/test_data"

    def assertEmpty(self, expr, msg=None):
        self.assertFalse(expr, msg)

    def assertNotEmpty(self, expr, msg=None):
        self.assertTrue(expr, msg)

    def assertMatch(self, expected_regex, expr, msg=None):
        self.assertRegex(expr, expected_regex, msg)

    def gen_tmp_file_path(self, suffix = None):
        with NamedTemporaryFile(mode='w+b', prefix='cypherpunkpay-test-', suffix=suffix) as file:
            return file.name
