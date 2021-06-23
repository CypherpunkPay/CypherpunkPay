import datetime
import logging as log
from decimal import Decimal

from test.unit.cypherpunkpay.cypherpunkpay_db_test_case import CypherpunkpayDBTestCase
from cypherpunkpay.db.sqlite_db import decimal_to_db_int8, db_int8_to_decimal
from cypherpunkpay.models.charge import ExampleCharge
from cypherpunkpay.models.dummy_store_order import DummyStoreOrder
from cypherpunkpay.models.user import User
from cypherpunkpay.tools.safe_uid import SafeUid


class SqliteDBTest(CypherpunkpayDBTestCase):

    def test_globals(self):
        initial_value = self.db.get_admin_unique_path_segment()
        self.assertIsNone(initial_value)

        example_value = 'IJOIjf983u23r23uhhhhQWDjff'
        self.db.insert_admin_unique_path_segment(example_value)
        read_value = self.db.get_admin_unique_path_segment()
        self.assertEqual(example_value, read_value)

    def test_users(self):
        user1 = User('example USERNAME', '$2y$12$V9dXY9O2calmARIWlVThqONRjU7fdMNKqaX3QvnL0syNeJLX19nve')
        self.db.insert(user1)

        user2 = User('user2', '$2y$12$G.8ra2jCHi0WwMDDV8vfZu1KFPBFbl0kb03GqbgLHmO.Xe5.BrgdC')
        self.db.insert(user2)

        user3 = User('third user', '$2y$15$lidG4gr29frMgPxC5n9Y0eGyZvDIYU.FpcHuaCsVFXLdVOgOvGtA.')
        self.db.insert(user3)

        # get_users_count()
        count = self.db.get_users_count()
        self.assertEqual(3, count)

        # get_users()
        users = self.db.get_users()

        self.assertEqual(3, len(users))

        ret1 = users[0]
        self.assertEqual(1, ret1.id)
        self.assertEqual(user1.username, ret1.username)
        self.assertEqual(user1.password_hash, ret1.password_hash)
        self.assertEqual(user1.created_at, ret1.created_at)
        self.assertEqual(user1.updated_at, ret1.updated_at)

        ret3 = users[2]
        self.assertEqual(3, ret3.id)
        self.assertEqual(user3.username, ret3.username)
        self.assertEqual(user3.password_hash, ret3.password_hash)
        self.assertEqual(user3.created_at, ret3.created_at)
        self.assertEqual(user3.updated_at, ret3.updated_at)

        # get_user_by_username()
        user = self.db.get_user_by_username('user2')
        self.assertEqual('user2', user.username)

        # save() / insert
        user4 = User('saved user', '$2y$12$V9dXY9O2calmARIWlVThqONRjU7fdMNKqaX3QvnL0syNeJLX19nve')
        self.db.save(user4)
        user = self.db.get_user_by_username('saved user')
        self.assertIsNotNone(user)

        # save() / update
        user = self.db.get_user_by_username('saved user')
        former_updated_at = user.updated_at
        user.username = 'updated user'
        self.db.save(user)
        user = self.db.get_user_by_username('updated user')   # can be found be new username
        self.assertLess(former_updated_at, user.updated_at)

        # delete_all_users()
        self.db.delete_all_users()
        ret = self.db.get_users_count()
        self.assertEqual(0, ret)

    def test_users_type_safety(self):
        invalid_user_username = User(1, '$2y$12$V9dXY9O2calmARIWlVThqONRjU7fdMNKqaX3QvnL0syNeJLX19nve')
        with self.assertRaises(AssertionError):
            self.db.insert(invalid_user_username)

        invalid_user_password_hash = User('example USERNAME', 1)
        with self.assertRaises(AssertionError):
            self.db.insert(invalid_user_password_hash)

        # Not a datetime
        invalid_user_created_at = User('example USERNAME', '$2y$12$V9dXY9O2calmARIWlVThqONRjU7fdMNKqaX3QvnL0syNeJLX19nve')
        invalid_user_created_at.created_at = 123
        with self.assertRaises(AssertionError):
            self.db.insert(invalid_user_created_at)

        # Not UTC
        invalid_user_created_at = User('example USERNAME', '$2y$12$V9dXY9O2calmARIWlVThqONRjU7fdMNKqaX3QvnL0syNeJLX19nve')
        invalid_user_created_at.created_at = datetime.datetime.now()
        with self.assertRaises(AssertionError):
            self.db.insert(invalid_user_created_at)

        # Not a datetime
        invalid_user_updated_at = User('example USERNAME', '$2y$12$V9dXY9O2calmARIWlVThqONRjU7fdMNKqaX3QvnL0syNeJLX19nve')
        invalid_user_updated_at.updated_at = 123
        with self.assertRaises(AssertionError):
            self.db.insert(invalid_user_updated_at)

        # Not UTC
        invalid_user_updated_at = User('example USERNAME', '$2y$12$V9dXY9O2calmARIWlVThqONRjU7fdMNKqaX3QvnL0syNeJLX19nve')
        invalid_user_updated_at.updated_at = datetime.datetime.now()
        with self.assertRaises(AssertionError):
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
            cc_received_total=Decimal('72.87654321'),

            pay_status='underpaid',
            status='expired',
            address_derivation_index=13
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
        self.assertEqual(3, ret)

        # get_charges()
        charges = self.db.get_charges()
        self.assertEqual(3, len(charges))

        ret2 = charges[1]
        self.assertEqual(charge2.uid, ret2.uid)
        self.assertEqual(charge2.total, ret2.total)
        self.assertEqual(charge2.currency, ret2.currency)
        self.assertEqual(charge2.time_to_pay_ms, ret2.time_to_pay_ms)
        self.assertEqual(charge2.time_to_complete_ms, ret2.time_to_complete_ms)
        self.assertEqual(charge2.cc_currency, ret2.cc_currency)
        self.assertEqual(charge2.cc_total, ret2.cc_total)
        self.assertEqual(charge2.cc_address, ret2.cc_address)
        self.assertEqual(charge2.cc_received_total, ret2.cc_received_total)
        self.assertEqual(charge2.pay_status, ret2.pay_status)
        self.assertEqual(charge2.status, ret2.status)
        self.assertEqual(charge2.address_derivation_index, ret2.address_derivation_index)
        self.assertEqual(charge2.confirmations, ret2.confirmations)
        self.assertEqual(charge2.status_fixed_manually, ret2.status_fixed_manually)
        self.assertEqual(charge2.block_explorer_1, ret2.block_explorer_1)
        self.assertEqual(charge2.block_explorer_2, ret2.block_explorer_2)
        self.assertEqual(charge2.subsequent_discrepancies, ret2.subsequent_discrepancies)

        self.assertEqual(charge2.created_at, ret2.created_at)
        self.assertEqual(charge2.updated_at, ret2.updated_at)

        # get_charge_by_uid()
        ret = self.db.get_charge_by_uid(charge2.uid)
        self.assertEqual(charge2.uid, ret.uid)

        # get_charges_by_status()
        ret = self.db.get_charges_by_status('expired')
        self.assertEqual(1, len(ret))
        self.assertEqual('expired', ret[0].status)

        # get_recently_activated_charges()
        ret = self.db.get_recently_activated_charges(delta=datetime.timedelta(microseconds=0))
        self.assertEqual(0, len(ret))
        ret = self.db.get_recently_activated_charges(delta=datetime.timedelta(minutes=1))
        self.assertEqual(3, len(ret))
        self.assertLess(ret[2].created_at, ret[1].created_at)
        self.assertLess(ret[1].created_at, ret[0].created_at)

        # get_last_charge()
        ret = self.db.get_last_charge()
        self.assertEqual(charge3.uid, ret.uid)

        # get_charges_for_merchant_notification()
        charge4 = ExampleCharge.create()
        charge4.status = 'completed'
        charge4.status_fixed_manually = True
        charge4.merchant_order_id = 'ord-1'
        self.db.insert(charge4)
        ret = self.db.get_charges_for_merchant_notification()
        self.assertEqual(1, len(ret))

        # save() / insert
        charge5 = ExampleCharge.create()
        self.db.save(charge5)
        inserted_charge = self.db.get_last_charge()
        self.assertEqual(charge5.uid, inserted_charge.uid)

        # save() / update
        charge = self.db.get_last_charge()
        charge.confirmations = 64321
        former_updated_at = charge.updated_at
        self.db.save(charge)
        updated_charge = self.db.get_charge_by_uid(charge.uid)
        self.assertEqual(64321, updated_charge.confirmations)
        self.assertLess(former_updated_at, updated_charge.updated_at)

    def test_coins(self):
        btc_height = self.db.get_blockchain_height('btc', 'mainnet')
        self.assertEqual(0, btc_height)

        xmr_height = self.db.get_blockchain_height('xmr', 'mainnet')
        self.assertEqual(0, xmr_height)

        self.db.update_blockchain_height('btc', 'testnet', 654_001)
        btc_height = self.db.get_blockchain_height('btc', 'testnet')
        self.assertEqual(654_001, btc_height)

        self.db.update_blockchain_height('xmr', 'stagenet', 2_954_001)
        xmr_height = self.db.get_blockchain_height('xmr', 'stagenet')
        self.assertEqual(2_954_001, xmr_height)

    def test_orders(self):
        order = DummyStoreOrder(uid=SafeUid.gen(), item_id=3, total='0.0097', currency='gbp')
        self.db.insert(order)

        order = self.db.get_order_by_uid(order.uid)
        self.assertEqual(3, order.item_id)
        self.assertEqual(Decimal('0.0097'), order.total)
        self.assertEqual('gbp', order.currency)

        order.payment_completed('200.34000001', 'BTC')
        self.db.save(order)
        self.assertEqual(Decimal('200.34000001'), order.cc_total)
        self.assertEqual('btc', order.cc_currency)

    def test_decimal_to_db_int8(self):
        self.assertEqual(None, decimal_to_db_int8(None))
        self.assertEqual(0, decimal_to_db_int8(Decimal('0')))
        self.assertEqual(100_000_000, decimal_to_db_int8(Decimal('1')))
        self.assertEqual(1, decimal_to_db_int8(Decimal('0.00000001')))
        self.assertEqual(1, decimal_to_db_int8(Decimal('0.0000000051')))
        self.assertEqual(0, decimal_to_db_int8(Decimal('0.0000000049')))
        self.assertEqual(123456789012345678, decimal_to_db_int8(Decimal('1234567890.12345678')))

    def test_db_int8_to_decimal(self):
        self.assertEqual(db_int8_to_decimal(0), Decimal('0'))
        self.assertEqual(db_int8_to_decimal(100_000_000), Decimal('1'))
        self.assertEqual(db_int8_to_decimal(1), Decimal('0.00000001'))
        self.assertEqual(db_int8_to_decimal(123456789012345678), Decimal('1234567890.12345678'))
