from tests.network.explorers.bitcoin.block_explorer_test import BlockExplorerTest

from cypherpunkpay.globals import *
from cypherpunkpay.net.http_client.dummy_http_client import DummyHttpClient
from cypherpunkpay.explorers.bitcoin.trezor_explorer import TrezorExplorer


class TrezorExplorerTest(BlockExplorerTest):

    def test_get_height_mainnet(self):
        be = TrezorExplorer(self.tor_http_client, btc_network='mainnet')
        self.assert_btc_mainnet_height(be)

    def test_get_height_testnet(self):
        be = TrezorExplorer(self.tor_http_client, btc_network='testnet')
        self.assert_btc_testnet_height(be)

    def test_get_address_credits_mainnet(self):
        be = TrezorExplorer(self.tor_http_client, btc_network='mainnet')
        credits = be.get_address_credits(
            address='bc1qwqdg6squsna38e46795at95yu9atm8azzmyvckulcc7kytlcckxswvvzej',
            current_height=0
        )
        self.assertNotEmpty(credits.all())

    def test_get_address_credits_testnet(self):
        be = TrezorExplorer(self.tor_http_client, btc_network='testnet')
        credits = be.get_address_credits(
            address='tb1q4cnvakxhuwrlfesn5uvj4haqp83t6zvpsxwzv8',
            current_height=0
        )
        self.assertEqual(1, len(credits.all()))

    def test_non_json_response(self):
        height = self.trezor_explorer(stub_response='not_json.txt').get_height()
        assert height is None
        height = self.trezor_explorer(stub_response=None).get_height()
        assert height is None

    def test_no_transactions(self):
        credits = self.trezor_explorer(
            stub_response='trezor_txs_bc1quwtrymfzavun8awsv9fqv36wlk0058puuw7mer.json'
        ).get_address_credits(
            address='bc1quwtrymfzavun8awsv9fqv36wlk0058puuw7mer',
            current_height=1
        )
        assert len(credits.all()) == 0

    def test_confirmed_skips_unrelated_utxo(self):
        credits = self.trezor_explorer(
            stub_response='trezor_txs_3K4J6FSPrpt4uxfhLEqitUeqipA5hR2zJN.json'
        ).get_address_credits(
            address='3K4J6FSPrpt4uxfhLEqitUeqipA5hR2zJN',
            current_height=569992
        )
        assert len(credits.all()) == 1
        credit = credits.all()[0]
        assert credit.value() == Decimal('0.02800000')
        assert credit.is_confirmed()
        assert not credit.is_unconfirmed()

    def test_confirmed_large_utxo(self):
        credits = self.trezor_explorer(
            stub_response='trezor_txs_1CgA8NopgG1Sg5rrsBkDo8LcT7wT6r7Z3T.json'
        ).get_address_credits(
            address='1CgA8NopgG1Sg5rrsBkDo8LcT7wT6r7Z3T',
            current_height=1000000
        )
        confirmed = credits.confirmed_1()
        assert len(confirmed) == 14
        total_credited = sum(map(lambda c: c.value(), confirmed))
        assert total_credited == Decimal('1.223911')

    def test_unconfirmed_non_replaceable(self):
        credits = self.trezor_explorer(
            stub_response='trezor_txs_bc1qkl6z6c8qz2v2luxv8ajj24t5ymqvex09f667q0.json'
        ).get_address_credits(
            address='bc1qkl6z6c8qz2v2luxv8ajj24t5ymqvex09f667q0',
            current_height=1
        )
        assert len(credits.all()) == 1
        credit = credits.all()[0]
        assert credit.value() == Decimal('0.06893409')
        assert credit.is_unconfirmed()
        assert credit.is_unconfirmed_non_replaceable()

    def test_unconfirmed_replaceable(self):
        # Not real data (manually created; scripts won't match address)
        credits = self.trezor_explorer(
            stub_response='trezor_txs_bc1q0uwu9upclerpj7hfwtg0kxrucjj5ssq5543mxc.json'
        ).get_address_credits(
            address='bc1q0uwu9upclerpj7hfwtg0kxrucjj5ssq5543mxc',
            current_height=1
        )
        assert len(credits.all()) == 1
        credit = credits.all()[0]
        assert credit.value() == Decimal('0.06893409')
        assert credit.is_unconfirmed_replaceable()

    def trezor_explorer(self, stub_response: [str, None]):
        return TrezorExplorer(http_client=StubHttpClient(stub_response), btc_network='mainnet')


class StubHttpClient(DummyHttpClient):

    def __init__(self, response_filename: str):
        self.response_filename = response_filename

    def get_text_or_None_on_error(self, url: str, privacy_context: str, verify=None) -> [str, None]:
        if self.response_filename is None:
            return None
        return (dir_of(__file__) / 'test_data' / 'trezor' / self.response_filename).read_text()
