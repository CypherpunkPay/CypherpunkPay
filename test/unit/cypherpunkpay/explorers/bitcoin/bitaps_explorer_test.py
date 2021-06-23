from pathlib import Path

from cypherpunkpay.common import *
from test.unit.cypherpunkpay.cypherpunkpay_test_case import CypherpunkpayTestCase
from cypherpunkpay.explorers.bitcoin.bitaps_explorer import BitapsExplorer
from cypherpunkpay.net.http_client.dummy_http_client import DummyHttpClient


class MockedHttpClient(DummyHttpClient):

    def __init__(self, response_filename: str):
        self.response_filename = response_filename

    def get_text_or_None_on_error(self, url: str, privacy_context: str) -> [str, None]:
        if self.response_filename is None:
            return None
        if 'unconfirmed' in url:
            path = self.response_filename.replace('{ifconfirmed}', 'unconfirmed')
        else:
            path = self.response_filename.replace('{ifconfirmed}', 'confirmed')
        return Path(f"{CypherpunkpayTestCase.examples_dir(__file__)}/bitaps/{path}").read_text()


class BitapsExplorerTest(CypherpunkpayTestCase):

    def test_non_json_response(self):
        height = self.mocked_explorer(response=None).get_height()
        self.assertIsNone(height)

    def test_empty(self):
        credits = self.mocked_explorer(
            response='bitaps_txs_bc1quwtrymfzavun8awsv9fqv36wlk0058puuw7mer_{ifconfirmed}.json').get_address_credits(
            address='bc1quwtrymfzavun8awsv9fqv36wlk0058puuw7mer',
            current_height=1
        )
        self.assertEmpty(credits.any())

    def test_confirmed_skips_unrelated_utxo(self):
        credits = self.mocked_explorer(
            response='bitaps_txs_3K4J6FSPrpt4uxfhLEqitUeqipA5hR2zJN_{ifconfirmed}.json').get_address_credits(
            address='3K4J6FSPrpt4uxfhLEqitUeqipA5hR2zJN',
            current_height=569992
        )
        self.assertTrue(len(credits.any()), 1)
        credit = credits.any()[0]
        self.assertEqual(Decimal('0.02800000'), credit.value())
        self.assertTrue(credit.is_confirmed())
        self.assertFalse(credit.is_unconfirmed())

    def test_confirmed_large_utxo(self):
        credits = self.mocked_explorer(
            response='bitaps_txs_1CgA8NopgG1Sg5rrsBkDo8LcT7wT6r7Z3T_{ifconfirmed}.json').get_address_credits(
            address='1CgA8NopgG1Sg5rrsBkDo8LcT7wT6r7Z3T',
            current_height=1000000
        )
        confirmed = credits.confirmed_1()
        self.assertEqual(14, len(confirmed))
        total_credited = sum(map(lambda c: c.value(), confirmed))
        self.assertEqual(Decimal('1.223911'), total_credited)

    def test_unconfirmed_non_replaceable(self):
        credits = self.mocked_explorer(
            response='bitaps_txs_bc1qkl6z6c8qz2v2luxv8ajj24t5ymqvex09f667q0_{ifconfirmed}.json').get_address_credits(
            address='bc1qkl6z6c8qz2v2luxv8ajj24t5ymqvex09f667q0',
            current_height=1
        )
        self.assertEqual(len(credits.any()), 1)
        credit = credits.any()[0]
        self.assertEqual(Decimal('0.06893409'), credit.value())
        self.assertTrue(credit.is_unconfirmed())
        self.assertTrue(credit.is_unconfirmed_non_replaceable())

    def test_unconfirmed_replaceable(self):
        # Not real data (manually created; scripts won't match address)
        credits = self.mocked_explorer(
            response='bitaps_txs_bc1q0uwu9upclerpj7hfwtg0kxrucjj5ssq5543mxc_{ifconfirmed}.json').get_address_credits(
            address='bc1q0uwu9upclerpj7hfwtg0kxrucjj5ssq5543mxc',
            current_height=1
        )
        self.assertEqual(len(credits.any()), 1)
        credit = credits.any()[0]
        self.assertEqual(Decimal('0.06893409'), credit.value())
        self.assertTrue(credit.is_unconfirmed())
        self.assertTrue(credit.is_unconfirmed_replaceable())

    def mocked_explorer(self, response: [str, None]):
        return BitapsExplorer(http_client=MockedHttpClient(response), btc_network='mainnet')
