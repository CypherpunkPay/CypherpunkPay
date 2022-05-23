from cypherpunkpay.globals import *
from cypherpunkpay import ExamplePriceTickers
from cypherpunkpay.db.sqlite_db import SqliteDB
from cypherpunkpay.models.charge import Charge
from cypherpunkpay.usecases.create_charge_uc import CreateChargeUC
from cypherpunkpay.usecases.pick_cryptocurrency_for_charge_uc import PickCryptocurrencyForChargeUC
from tests.network.network_test_case import CypherpunkpayNetworkTestCase
from tests.unit.config.example_config import ExampleConfig


class ExampleMoneroConfig(ExampleConfig):

    def xmr_main_address(self) -> str:
        return '5BKTP2n9Tto6fJ25fv5seHUwuyiSFk2kZJV5LKnQkXp4DknK1e28tPGiEWqbLMJ4wWamGACRW7aTZEXiqEsbgJGfK2QffLz'

    def xmr_secret_view_key(self) -> str:
        return '1543738e3ff094c144ed6697a26beb313c765ffd368b781bd4602a4c6153c305'


class FetchMoneroTxsFromOpenNodeUCTest(CypherpunkpayNetworkTestCase):

    def setup_method(self):
        super().setup_method()
        self.db = SqliteDB(self.gen_tmp_file_path('.sqlite3'))
        self.db.connect()
        self.db.migrate()

    def teardown_method(self):
        self.db.disconnect()
        super().teardown_method()

    def test_when_uptodate_fetch_nothing(self):
        charge = self.insert_xmr_charge(total='0.00000001', created_at='2022-02-11 00:00:00')
        pprint(charge.cc_address)

        charge = self.insert_xmr_charge(total='10', created_at='2022-02-11 00:00:00')
        pprint(charge.cc_address)

        charge = self.insert_xmr_charge(total='10', created_at='2022-02-11 00:00:00')
        pprint(charge.cc_address)

        # FetchMoneroTxsFromOpenNodeUC(
        #     host=self.XMR_STAGENET_REMOTE_HOST,
        #     port=self.XMR_STAGENET_REMOTE_PORT,
        #     db=db,
        # )

    def insert_xmr_charge(self, total: str, created_at=None, activated_at=None) -> Charge:
        if isinstance(created_at, str):
            created_at = utc_from_iso(created_at)
        if isinstance(activated_at, str):
            activated_at = utc_from_iso(activated_at)
        if activated_at is None:
            activated_at = created_at
        charge = CreateChargeUC(
            total=total,
            currency='xmr',
            db=self.db,
            config=ExampleMoneroConfig(),
            price_tickers=ExamplePriceTickers(),
            qr_cache={}
        ).exec()
        charge = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='xmr',
            db=self.db,
            config=ExampleMoneroConfig(),
            price_tickers=ExamplePriceTickers()
        ).exec()
        if created_at:
            charge.created_at = created_at
        if activated_at:
            charge.activated_at = activated_at
        self.db.save(charge)
        return charge
