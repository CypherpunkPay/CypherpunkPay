from cypherpunkpay.globals import *
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.monero.monero_tx_db import MoneroTxDb
from cypherpunkpay.usecases.calc_monero_address_credits_uc import CalcMoneroAddressCreditsUC
from tests.network.network_test_case import CypherpunkpayNetworkTestCase


class CalcMoneroAddressCreditsUCTest(CypherpunkpayNetworkTestCase):

    YEAR_2022: datetime.datetime = datetime.datetime(year=2022, month=1, day=1, hour=0, minute=0, second=0)
    MAX_HEIGHT = 3_000_000

    XMR_STAGENET_MAIN_ADDRESS = '5BKTP2n9Tto6fJ25fv5seHUwuyiSFk2kZJV5LKnQkXp4DknK1e28tPGiEWqbLMJ4wWamGACRW7aTZEXiqEsbgJGfK2QffLz'
    XMR_STAGENET_MAIN_ADDRESS_VIEW_SECRET = '1543738e3ff094c144ed6697a26beb313c765ffd368b781bd4602a4c6153c305'

    XMR_STAGENET_SUBADDRESS_1 = '74AVKsVDK8XPRjK6rBdwL5RVvjTgWvEudeDAcEpcVf4zYfNrDaz5K58AUbYTpUtahfNYeCnQAsebrGkevMvSeiKWNBFLdoA'

    def test_empty_tx_db(self):
        empty_tx_db = MoneroTxDb()
        uc = CalcMoneroAddressCreditsUC(
            monero_tx_db=empty_tx_db,
            since=self.YEAR_2022,
            subaddress=self.XMR_STAGENET_MAIN_ADDRESS,
            current_height=self.MAX_HEIGHT,
            secret_view_key=self.XMR_STAGENET_MAIN_ADDRESS_VIEW_SECRET
        )
        address_credits: AddressCredits = uc.exec()
        assert len(address_credits.all()) == 0

    def test_main_address(self):
        from monero.daemon import Daemon
        daemon = Daemon(host='stagenet.community.rino.io', port=38081)
        txs = daemon.transactions([
            '26cb0bde5fe0ebe57806ee18d87d20ac76bf5825733b12edaa8f422e2d56bd03',  #  no: same account, another subaddress
            '640b10fcbd8327ebca68e0932d0ad95ba91c2bbe8ab59c96526822ce6859cbcf',  #  yes: the rest of +9.99995357 XMR from payment to another subaddress
            'd65d05db90da239d4bbc2ae7ec711aa2da45c0eb62bce0078f94e90000a24362',  #  yes: +10 XMR
            'de035fd86ebdf7e465ba66b6cca19767d55cbad352148d93ccb0ccceb6410ba7',  #  no: some random tx
            'bc9e7c95444d063977a11eb7f658af1d3b30ec18f0a08830cdde1e329edc98e3',  #  no: some random tx
        ])

        monero_tx_db = MoneroTxDb()
        monero_tx_db.confirmed_txs = txs

        uc = CalcMoneroAddressCreditsUC(
            monero_tx_db=monero_tx_db,
            since=self.YEAR_2022,
            subaddress=self.XMR_STAGENET_MAIN_ADDRESS,
            current_height=self.MAX_HEIGHT,
            secret_view_key=self.XMR_STAGENET_MAIN_ADDRESS_VIEW_SECRET
        )
        address_credits: AddressCredits = uc.exec()
        pprint(address_credits.all())
        assert len(address_credits.confirmed_n(20)) == 2
        assert sum(map(lambda credit: credit.value(), address_credits.all())) == Decimal('19.99995357')
        daemon._backend.session.close()

    def test_subaddress(self):
        from monero.daemon import Daemon
        daemon = Daemon(host='stagenet.community.rino.io', port=38081)
        txs = daemon.transactions([
            '26cb0bde5fe0ebe57806ee18d87d20ac76bf5825733b12edaa8f422e2d56bd03',  # yes: +10 XMR
            '640b10fcbd8327ebca68e0932d0ad95ba91c2bbe8ab59c96526822ce6859cbcf',  # yes: +0.00000007 XMR
            'd65d05db90da239d4bbc2ae7ec711aa2da45c0eb62bce0078f94e90000a24362',  #  no: same account, another subaddress (primary)
            'de035fd86ebdf7e465ba66b6cca19767d55cbad352148d93ccb0ccceb6410ba7',  #  no: some random tx
            'bc9e7c95444d063977a11eb7f658af1d3b30ec18f0a08830cdde1e329edc98e3',  #  no: some random tx
        ])
        monero_tx_db = MoneroTxDb()
        monero_tx_db.confirmed_txs = txs

        uc = CalcMoneroAddressCreditsUC(
            monero_tx_db=monero_tx_db,
            since=self.YEAR_2022,
            subaddress=self.XMR_STAGENET_SUBADDRESS_1,
            current_height=self.MAX_HEIGHT,
            secret_view_key=self.XMR_STAGENET_MAIN_ADDRESS_VIEW_SECRET
        )
        address_credits: AddressCredits = uc.exec()
        assert len(address_credits.confirmed_n(20)) == 2
        assert sum(map(lambda credit: credit.value(), address_credits.all())) == Decimal('10.00000007')
        daemon._backend.session.close()
