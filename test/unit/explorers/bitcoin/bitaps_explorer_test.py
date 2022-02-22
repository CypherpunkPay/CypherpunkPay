from test.unit.test_case import *
from cypherpunkpay.explorers.bitcoin.bitaps_explorer import BitapsExplorer
from cypherpunkpay.net.http_client.dummy_http_client import DummyHttpClient


class StubHttpClient(DummyHttpClient):

    def __init__(self, response_filename: str):
        self.response_filename = response_filename

    def get_text_or_None_on_error(self, url: str, privacy_context: str, verify=None) -> [str, None]:
        if self.response_filename is None:
            return None
        if 'unconfirmed' in url:
            filename = self.response_filename.replace('ifconfirmed', 'unconfirmed')
        else:
            filename = self.response_filename.replace('ifconfirmed', 'confirmed')
        return (this_dir(__file__) / 'test_data' / 'bitaps' / filename).read_text()


class BitapsExplorerTest(CypherpunkpayTestCase):

    def test_non_json_response(self):
        height = self.bitaps_explorer(response='not_json.txt').get_height()
        assert height is None
        height = self.bitaps_explorer(response=None).get_height()
        assert height is None

    def test_no_transactions(self):
        credits = self.bitaps_explorer(
            response='bitaps_txs_bc1quwtrymfzavun8awsv9fqv36wlk0058puuw7mer_ifconfirmed.json'
        ).get_address_credits(
            address='bc1quwtrymfzavun8awsv9fqv36wlk0058puuw7mer',
            current_height=1
        )
        assert is_empty(credits.all())

    def test_confirmed_skips_unrelated_utxo(self):
        credits = self.bitaps_explorer(
            response='bitaps_txs_3K4J6FSPrpt4uxfhLEqitUeqipA5hR2zJN_ifconfirmed.json'
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
        credits = self.bitaps_explorer(
            response='bitaps_txs_1CgA8NopgG1Sg5rrsBkDo8LcT7wT6r7Z3T_ifconfirmed.json'
        ).get_address_credits(
            address='1CgA8NopgG1Sg5rrsBkDo8LcT7wT6r7Z3T',
            current_height=1000000
        )
        confirmed = credits.confirmed_1()
        total_credited = sum(map(lambda c: c.value(), confirmed))
        assert len(confirmed) == 14
        assert total_credited == Decimal('1.223911')

    def test_unconfirmed_non_replaceable(self):
        credits = self.bitaps_explorer(
            response='bitaps_txs_bc1qkl6z6c8qz2v2luxv8ajj24t5ymqvex09f667q0_ifconfirmed.json'
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
        credits = self.bitaps_explorer(
            response='bitaps_txs_bc1q0uwu9upclerpj7hfwtg0kxrucjj5ssq5543mxc_ifconfirmed.json'
        ).get_address_credits(
            address='bc1q0uwu9upclerpj7hfwtg0kxrucjj5ssq5543mxc',
            current_height=1
        )
        assert len(credits.all()) == 1
        credit = credits.all()[0]
        assert credit.value() == Decimal('0.06893409')
        assert credit.is_unconfirmed()
        assert credit.is_unconfirmed_replaceable()

    def bitaps_explorer(self, response: [str, None]):
        return BitapsExplorer(http_client=StubHttpClient(response), btc_network='mainnet')
