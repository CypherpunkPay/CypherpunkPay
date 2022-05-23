from monero.transaction import Transaction

from cypherpunkpay.monero.monero_address_transactions_db import MoneroAddressTransactionsDB
from tests.unit.test_case import *


class MoneroAddressTransactionsDBTest(CypherpunkpayTestCase):

    XMR_STAGENET_MAIN_ADDRESS = '5BKTP2n9Tto6fJ25fv5seHUwuyiSFk2kZJV5LKnQkXp4DknK1e28tPGiEWqbLMJ4wWamGACRW7aTZEXiqEsbgJGfK2QffLz'

    XMR_STAGENET_MAIN_ADDRESS_VIEW_PUBLIC = '419a1053fd5f7ff6841b971f66100dc9db469dd08a64a850e37e9b9d85c6a89f'
    XMR_STAGENET_MAIN_ADDRESS_VIEW_SECRET = '1543738e3ff094c144ed6697a26beb313c765ffd368b781bd4602a4c6153c305'

    XMR_STAGENET_MAIN_ADDRESS_SPEND_PUBLIC = 'fa603877c6149421d71ebe095a90aaa71538d438a7f77a6887c0cb44e6ab294c'
    XMR_STAGENET_MAIN_ADDRESS_SPEND_SECRET = '27499ed0228f443efba2a9b4307ed459cb0377d0cef77359c4e0171c4ce1a10e'

    # This belongs to us
    STEALTH_PUBLIC_1 = '53c2d7b08dc7ca09947876fb0d3e57f0863a856fa711762c08deabeb9a196464'
    # This is rest for the sender
    STEALTH_PUBLIC_2 = '0b5cd6caee5a6f9b99f2b47ada3094d80147fe8044f197d8c7f640ee4f585d58'

    XMR_PROJECT_DONATION_ADDRESS = '888tNkZrPN6JsEgekjMnABU4TBzc2Dt29EPAvkRxbANsAnjyPbb3iQ1YBRk1UXcdRsiKc9dhwMVgN5S9cQUiyoogDavup3H'

    def test_when_unknown_address_return_empty_list(self):
        atx = MoneroAddressTransactionsDB(filepath=self.gen_tmp_file_path())
        txs = atx.get_transactions(self.XMR_PROJECT_DONATION_ADDRESS)
        assert len(txs) == 0

    def test_return_added_transaction(self):
        tmp_path = self.gen_tmp_file_path()

        atx = MoneroAddressTransactionsDB(filepath=tmp_path)
        tx0 = self.daemon_fetch_txs('d65d05db90da239d4bbc2ae7ec711aa2da45c0eb62bce0078f94e90000a24362')[0]
        atx.add_transaction(self.XMR_STAGENET_MAIN_ADDRESS, tx0)
        atx.close()

        atx_reloaded = MoneroAddressTransactionsDB(filepath=tmp_path)

        txs = atx_reloaded.get_transactions(self.XMR_STAGENET_MAIN_ADDRESS)

        assert len(txs) == 1
        tx1: Transaction = txs[0]
        assert tx1.hash == tx0.hash
        assert tx1.height == tx0.height
        assert tx1.json == tx0.json
        assert tx1.outputs() == tx0.outputs()

    def test_return_multiple_transactions(self):
        tmp_path = self.gen_tmp_file_path()

        atx = MoneroAddressTransactionsDB(filepath=tmp_path)

        tx_a = self.daemon_fetch_txs('d65d05db90da239d4bbc2ae7ec711aa2da45c0eb62bce0078f94e90000a24362')[0]
        atx.add_transaction(self.XMR_STAGENET_MAIN_ADDRESS, tx_a)

        tx_b = self.daemon_fetch_txs('640b10fcbd8327ebca68e0932d0ad95ba91c2bbe8ab59c96526822ce6859cbcf')[0]
        atx.add_transaction(self.XMR_STAGENET_MAIN_ADDRESS, tx_b)

        atx.close()

        atx_reloaded = MoneroAddressTransactionsDB(filepath=tmp_path)

        txs = atx_reloaded.get_transactions(self.XMR_STAGENET_MAIN_ADDRESS)

        assert len(txs) == 2

        tx_a1: Transaction = txs[0]
        assert tx_a1.hash == tx_a.hash

        tx_b1: Transaction = txs[1]
        assert tx_b1.hash == tx_b.hash

    def test_when_deleted_address_return_empty_list(self):
        tmp_path = self.gen_tmp_file_path()

        atx = MoneroAddressTransactionsDB(filepath=tmp_path)

        tx_a = self.daemon_fetch_txs('d65d05db90da239d4bbc2ae7ec711aa2da45c0eb62bce0078f94e90000a24362')[0]
        atx.add_transaction(self.XMR_STAGENET_MAIN_ADDRESS, tx_a)

        atx.delete(self.XMR_STAGENET_MAIN_ADDRESS)
        atx.delete(self.XMR_STAGENET_MAIN_ADDRESS)
        txs = atx.get_transactions('d65d05db90da239d4bbc2ae7ec711aa2da45c0eb62bce0078f94e90000a24362')

        assert len(txs) == 0

    def daemon_fetch_txs(self, tx_hashes) -> List[Transaction]:
        from monero.daemon import Daemon
        daemon = Daemon(host='stagenet.community.rino.io', port=38081)
        txs = daemon.transactions(tx_hashes)
        daemon._backend.session.close()
        return txs
