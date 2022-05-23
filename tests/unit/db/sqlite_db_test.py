import pytest

from tests.unit.db_test_case import CypherpunkpayDBTestCase

from cypherpunkpay.globals import *
from cypherpunkpay.db.sqlite_db import decimal_to_db_int8, db_int8_to_decimal
from cypherpunkpay.models.charge import ExampleCharge
from cypherpunkpay.models.dummy_store_order import DummyStoreOrder
from cypherpunkpay.models.user import User
from cypherpunkpay.tools.safe_uid import SafeUid


class SqliteDBTest(CypherpunkpayDBTestCase):

    def test_globals(self):
        initial_value = self.db.get_admin_unique_path_segment()
        assert initial_value is None

        example_value = 'IJOIjf983u23r23uhhhhQWDjff'
        self.db.insert_admin_unique_path_segment(example_value)
        read_value = self.db.get_admin_unique_path_segment()
        assert read_value == example_value

    def test_users(self):
        user1 = User('example USERNAME', '$2y$12$V9dXY9O2calmARIWlVThqONRjU7fdMNKqaX3QvnL0syNeJLX19nve')
        self.db.insert(user1)

        user2 = User('user2', '$2y$12$G.8ra2jCHi0WwMDDV8vfZu1KFPBFbl0kb03GqbgLHmO.Xe5.BrgdC')
        self.db.insert(user2)

        user3 = User('third user', '$2y$15$lidG4gr29frMgPxC5n9Y0eGyZvDIYU.FpcHuaCsVFXLdVOgOvGtA.')
        self.db.insert(user3)

        # get_users_count()
        count = self.db.get_users_count()
        assert count == 3

        # get_users()
        users = self.db.get_users()

        assert len(users) == 3

        ret1 = users[0]
        assert ret1.id == 1
        assert ret1.username == user1.username
        assert ret1.password_hash == user1.password_hash
        assert ret1.created_at == user1.created_at
        assert ret1.updated_at == user1.updated_at

        ret3 = users[2]
        assert ret3.id == 3
        assert ret3.username == user3.username
        assert ret3.password_hash == user3.password_hash
        assert ret3.created_at == user3.created_at
        assert ret3.updated_at == user3.updated_at

        # get_user_by_username()
        user = self.db.get_user_by_username('user2')
        assert user.username == 'user2'

        # save() / insert
        user4 = User('saved user', '$2y$12$V9dXY9O2calmARIWlVThqONRjU7fdMNKqaX3QvnL0syNeJLX19nve')
        self.db.save(user4)
        user = self.db.get_user_by_username('saved user')
        assert user
        assert user.username == 'saved user'
        assert user.created_at  # is set

        # save() / update
        user = self.db.get_user_by_username('saved user')
        former_updated_at = user.updated_at
        user.username = 'updated user'
        self.db.save(user)
        user = self.db.get_user_by_username('updated user')   # can be found be new username
        assert former_updated_at < user.updated_at            # updated_at got updated

        # delete_all_users()
        self.db.delete_all_users()
        ret = self.db.get_users_count()
        assert ret == 0

    def test_users_type_safety(self):
        invalid_user_username = User(1, '$2y$12$V9dXY9O2calmARIWlVThqONRjU7fdMNKqaX3QvnL0syNeJLX19nve')
        with pytest.raises(AssertionError):
            self.db.insert(invalid_user_username)

        invalid_user_password_hash = User('example USERNAME', 1)
        with pytest.raises(AssertionError):
            self.db.insert(invalid_user_password_hash)

        # Not a datetime
        invalid_user_created_at = User('example USERNAME', '$2y$12$V9dXY9O2calmARIWlVThqONRjU7fdMNKqaX3QvnL0syNeJLX19nve')
        invalid_user_created_at.created_at = 123
        with pytest.raises(AssertionError):
            self.db.insert(invalid_user_created_at)

        # Not UTC
        invalid_user_created_at = User('example USERNAME', '$2y$12$V9dXY9O2calmARIWlVThqONRjU7fdMNKqaX3QvnL0syNeJLX19nve')
        invalid_user_created_at.created_at = datetime.datetime.now()
        with pytest.raises(AssertionError):
            self.db.insert(invalid_user_created_at)

        # Not a datetime
        invalid_user_updated_at = User('example USERNAME', '$2y$12$V9dXY9O2calmARIWlVThqONRjU7fdMNKqaX3QvnL0syNeJLX19nve')
        invalid_user_updated_at.updated_at = 123
        with pytest.raises(AssertionError):
            self.db.insert(invalid_user_updated_at)

        # Not UTC
        invalid_user_updated_at = User('example USERNAME', '$2y$12$V9dXY9O2calmARIWlVThqONRjU7fdMNKqaX3QvnL0syNeJLX19nve')
        invalid_user_updated_at.updated_at = datetime.datetime.now()
        with pytest.raises(AssertionError):
            self.db.insert(invalid_user_updated_at)

    def test_charges(self):
        charge1 = ExampleCharge.create()
        self.db.insert(charge1)

        charge2 = ExampleCharge.create(
            total=Decimal('5.99'),
            currency='eur',
            timeout_ms=10*1000,
            timeout_to_complete_ms=20*1000,
            merchant_order_id='xxUU99-!@#',

            cc_currency='xmr',
            cc_total=Decimal('97372.87654321'),
            cc_address='888tNkZrPN6JsEgekjMnABU4TBzc2Dt29EPAvkRxbANsAnjyPbb3iQ1YBRk1UXcdRsiKc9dhwMVgN5S9cQUiyoogDavup3H',
            cc_lightning_payment_request='lnbc27560n1psdhzaepp5p36vfwhvk0u6fjcqnjafmg5hqqqhdtyk74ayr3gp7x02jmp347dqdpu2pskjepqw3hjqjfq7z060gfqu2pt76t5vdhkjm3q9p8hyer9wgsyj3p6yq5scqzpgxqzjhsp5thcs724yw5yvcl0lqt4xuxlhz77dpa9f28m2zevt3q0xfwa5se8s9qyyssquklk9nqcmfljlhxfy0cumhjly3lpymnzrphmu3rp37met82wskzru5ee3a4np4ukpu298zs3gxk3xdu3afvsd7we2yfjvx9k39eaycgq2ylqgg',
            cc_received_total=Decimal('72.87654321'),

            pay_status='underpaid',
            status='expired',
            address_derivation_index=13,

            beneficiary='SQLite',
            what_for='Further Development'
        )
        charge2.confirmations = 2
        charge2.status_fixed_manually = True
        charge2.block_explorer_1 = 'cypherpunkpay.explorers.bitcoin.blockstream_explorer BlockstreamExplorer'
        charge2.block_explorer_2 = 'cypherpunkpay.explorers.bitcoin.trezor_explorer TrezorExplorer'
        charge2.subsequent_discrepancies = 10
        self.db.insert(charge2)

        charge3 = ExampleCharge.create()
        self.db.insert(charge3)

        # get_charges_count()
        ret = self.db.get_charges_count()
        assert ret == 3

        # get_charges()
        charges = self.db.get_charges()
        assert len(charges) == 3

        ret2 = charges[1]
        assert charge2.uid == ret2.uid
        assert charge2.total == ret2.total
        assert charge2.currency == ret2.currency
        assert charge2.time_to_pay_ms == ret2.time_to_pay_ms
        assert charge2.time_to_complete_ms == ret2.time_to_complete_ms
        assert charge2.cc_currency == ret2.cc_currency
        assert charge2.cc_total == ret2.cc_total
        assert charge2.cc_address == ret2.cc_address
        assert charge2.cc_lightning_payment_request == ret2.cc_lightning_payment_request
        assert charge2.cc_received_total == ret2.cc_received_total
        assert charge2.pay_status == ret2.pay_status
        assert charge2.status == ret2.status
        assert charge2.address_derivation_index == ret2.address_derivation_index
        assert charge2.confirmations == ret2.confirmations
        assert charge2.status_fixed_manually == ret2.status_fixed_manually
        assert charge2.block_explorer_1 == ret2.block_explorer_1
        assert charge2.block_explorer_2 == ret2.block_explorer_2
        assert charge2.subsequent_discrepancies == ret2.subsequent_discrepancies
        assert charge2.beneficiary == ret2.beneficiary
        assert charge2.what_for == ret2.what_for

        assert charge2.created_at == ret2.created_at
        assert charge2.updated_at == ret2.updated_at

        # get_charge_by_uid()
        ret = self.db.get_charge_by_uid(charge2.uid)
        assert charge2.uid == ret.uid

        # get_charges_by_status()
        ret = self.db.get_charges_by_status('expired')
        assert len(ret) == 1
        assert ret[0].status == 'expired'

        # get_recently_activated_charges()
        ret = self.db.get_recently_activated_charges(delta=datetime.timedelta(microseconds=0))
        assert len(ret) == 0
        ret = self.db.get_recently_activated_charges(delta=datetime.timedelta(minutes=1))
        assert len(ret) == 3
        assert ret[2].created_at < ret[1].created_at
        assert ret[1].created_at < ret[0].created_at

        # get_last_charge()
        ret = self.db.get_last_charge()
        assert ret.uid == charge3.uid

        # get_charges_for_merchant_notification()
        charge4 = ExampleCharge.create()
        charge4.status = 'completed'
        charge4.status_fixed_manually = True
        charge4.merchant_order_id = 'ord-1'
        self.db.insert(charge4)
        ret = self.db.get_charges_for_merchant_notification(statuses=['completed'])
        assert len(ret) == 1

        # save() / insert
        charge5 = ExampleCharge.create()
        self.db.save(charge5)
        inserted_charge = self.db.get_last_charge()
        assert inserted_charge.uid == charge5.uid

        # save() / update
        charge = self.db.get_last_charge()
        charge.confirmations = 64321
        former_updated_at = charge.updated_at
        self.db.save(charge)
        updated_charge = self.db.get_charge_by_uid(charge.uid)
        assert updated_charge.confirmations == 64321
        assert former_updated_at < updated_charge.updated_at

    def test_coins(self):
        btc_height = self.db.get_blockchain_height('btc', 'mainnet')
        assert btc_height == 0

        xmr_height = self.db.get_blockchain_height('xmr', 'mainnet')
        assert xmr_height == 0

        self.db.update_blockchain_height('btc', 'testnet', 654_001)
        btc_height = self.db.get_blockchain_height('btc', 'testnet')
        assert btc_height == 654_001

        self.db.update_blockchain_height('xmr', 'stagenet', 2_954_001)
        xmr_height = self.db.get_blockchain_height('xmr', 'stagenet')
        assert xmr_height == 2_954_001

    def test_orders(self):
        order = DummyStoreOrder(uid=SafeUid.gen(), item_id=3, total='0.0097', currency='gbp')
        self.db.insert(order)

        order = self.db.get_order_by_uid(order.uid)
        assert order.item_id == 3
        assert order.total == Decimal('0.0097')
        assert order.currency == 'gbp'

        order.payment_completed('200.34000001', 'BTC')
        self.db.save(order)
        assert order.cc_total == Decimal('200.34000001')
        assert order.cc_currency == 'btc'

    def test_decimal_to_db_int8(self):
        assert decimal_to_db_int8(None) is None
        assert decimal_to_db_int8(Decimal('0')) == 0
        assert decimal_to_db_int8(Decimal('1')) == 100_000_000
        assert decimal_to_db_int8(Decimal('0.00000001')) == 1
        assert decimal_to_db_int8(Decimal('0.0000000051')) == 1
        assert decimal_to_db_int8(Decimal('0.0000000049')) == 0
        assert decimal_to_db_int8(Decimal('1234567890.12345678')) == 123456789012345678

    def test_db_int8_to_decimal(self):
        assert db_int8_to_decimal(0) == Decimal('0')
        assert db_int8_to_decimal(100_000_000) == Decimal('1')
        assert db_int8_to_decimal(1) == Decimal('0.00000001')
        assert db_int8_to_decimal(123456789012345678) == Decimal('1234567890.12345678')
