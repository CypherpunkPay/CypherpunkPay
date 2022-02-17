import os
from decimal import Decimal
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.case import TestCase

import pytest


class CypherpunkpayTestCase(TestCase):

    ONE_SATOSHI = Decimal('0.00000001')
    ONE_CENT = Decimal('0.01')

    EXAMPLE_PAYMENT_REQUEST_TESTNET = 'lntb20m1pvjluezhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqspp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfpp3x9et2e20v6pu37c5d9vax37wxq72un98kmzzhznpurw9sgl2v0nklu2g4d0keph5t7tj9tcqd8rexnd07ux4uv2cjvcqwaxgj7v4uwn5wmypjd5n69z2xm3xgksg28nwht7f6zspwp3f9t'

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

    def gen_tmp_file_path(self, suffix=None):
        with NamedTemporaryFile(mode='w+b', prefix='cypherpunkpay-test-', suffix=suffix) as file:
            return file.name
