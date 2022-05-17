from tests.unit.test_case import *
from tests.network.network_test_case import CypherpunkpayNetworkTestCase

from cypherpunkpay.db.monero_address_transactions_db import MoneroAddressTransactionsDB


# This test is a temporary scratch pad,
class MoneroTest(CypherpunkpayNetworkTestCase):

    XMR_STAGENET_MAIN_ADDRESS = '5BKTP2n9Tto6fJ25fv5seHUwuyiSFk2kZJV5LKnQkXp4DknK1e28tPGiEWqbLMJ4wWamGACRW7aTZEXiqEsbgJGfK2QffLz'

    XMR_STAGENET_MAIN_ADDRESS_VIEW_PUBLIC = '419a1053fd5f7ff6841b971f66100dc9db469dd08a64a850e37e9b9d85c6a89f'
    XMR_STAGENET_MAIN_ADDRESS_VIEW_SECRET = '1543738e3ff094c144ed6697a26beb313c765ffd368b781bd4602a4c6153c305'

    XMR_STAGENET_MAIN_ADDRESS_SPEND_PUBLIC = 'fa603877c6149421d71ebe095a90aaa71538d438a7f77a6887c0cb44e6ab294c'
    XMR_STAGENET_MAIN_ADDRESS_SPEND_SECRET = '27499ed0228f443efba2a9b4307ed459cb0377d0cef77359c4e0171c4ce1a10e'

    # This belongs to us
    STEALTH_PUBLIC_1 = '53c2d7b08dc7ca09947876fb0d3e57f0863a856fa711762c08deabeb9a196464'
    # This is rest for the sender
    STEALTH_PUBLIC_2 = '0b5cd6caee5a6f9b99f2b47ada3094d80147fe8044f197d8c7f640ee4f585d58'

    def test_monero_address_transactions(self):
        atx = MoneroAddressTransactionsDB(filepath=self.gen_tmp_file_path())
        # TODO: working on this
        # atx.get_transactions(address)
        # atx.add_transaction(address, tx)
        # atx.delete(address)

    def test_txo_recognized(self):
        from monero.daemon import Daemon
        from monero.wallet import Wallet
        from monero.backends.offline import OfflineWallet

        offline_wallet = OfflineWallet(
            address=self.XMR_STAGENET_MAIN_ADDRESS,
            view_key=self.XMR_STAGENET_MAIN_ADDRESS_VIEW_SECRET,
            spend_key=self.XMR_STAGENET_MAIN_ADDRESS_SPEND_SECRET
        )
        wallet = Wallet(backend=offline_wallet)

        daemon = Daemon(host=self.XMR_STAGENET_REMOTE_HOST, port=self.XMR_STAGENET_REMOTE_PORT)
        tx = daemon.transactions("d65d05db90da239d4bbc2ae7ec711aa2da45c0eb62bce0078f94e90000a24362")[0]
        #tx = daemon.transactions("26cb0bde5fe0ebe57806ee18d87d20ac76bf5825733b12edaa8f422e2d56bd03")[0]

        pprint(tx.__dict__)

        outs = tx.outputs(wallet=wallet)
        pprint(outs[0])

        daemon._backend.session.close()
