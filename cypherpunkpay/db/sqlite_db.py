import sqlite3
import threading
from sqlite3 import Cursor

from cypherpunkpay.common import *
from cypherpunkpay.db.db import DB
from cypherpunkpay.db.sqlite_type_assertions import assert_charge_types, assert_user_types
from cypherpunkpay.models.charge import Charge
from cypherpunkpay.models.user import User
from cypherpunkpay.models.dummy_store_order import DummyStoreOrder


class SqliteDB(DB):

    _db_file_path: str
    _db: sqlite3.Connection

    def __init__(self, db_file_path: str):
        self._db_file_path = db_file_path
        self.lock = threading.RLock()

    def __enter__(self):
        with self.lock:
            log.info(f'Connecting to database {self._db_file_path}')
            self._db = sqlite3.connect(
                self._db_file_path,
                isolation_level=None,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                check_same_thread=False
            )
            self._db.row_factory = sqlite3.Row  # enable accessing rows by column name
            return self

    def __exit__(self):
        with self.lock:
            self._db.close()

    def migrate(self) -> None:
        with self.lock:
            log.info(f'Migrating database {self._db_file_path} ...')
            from yoyo import read_migrations, get_backend
            backend = get_backend(f'sqlite:///{self._db_file_path}')
            migrations = read_migrations(os.path.join(os.path.dirname(__file__), 'migrations'))
            with backend.lock():
                # Apply any outstanding migrations
                backend.apply_migrations(backend.to_apply(migrations))
            log.info("Migration done.")

    def reset_for_tests(self) -> None:
        with self.lock:
            self.disconnect()
            remove_file_if_present(self._db_file_path)
            self.connect()
            self.migrate()

    def insert(self, obj: [User, Charge, DummyStoreOrder]):
        with self.lock:
            if isinstance(obj, User):
                user: User = obj
                sql = """
                    INSERT
                        INTO users (username, password_hash, created_at, updated_at)
                        VALUES (?, ?, ?, ?)
                """
                assert_user_types(user)
                values = (user.username, user.password_hash, user.created_at, user.updated_at)
            if isinstance(obj, Charge):
                charge: Charge = obj
                sql = f"""
                    INSERT
                        INTO charges ({self.CHARGE_COLUMNS})
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                assert_charge_types(charge)
                values = self._charge_values(charge)
            if isinstance(obj, DummyStoreOrder):
                order: DummyStoreOrder = obj
                sql = f"""
                    INSERT
                        INTO dummy_store_orders ({self.DUMMY_STORE_ORDERS_COLUMNS})
                        VALUES (?, ?, ?, ?, ?, ?)
                """
                values = self._dummy_store_order_values(order)

            self._db.execute(sql, values)
            self._db.commit()

    def save(self, obj: [User, Charge, DummyStoreOrder]) -> None:
        with self.lock:
            if isinstance(obj, User):
                user: User = obj
                if self.exists(user):
                    user.updated_at = utc_now()
                    sql = """
                        UPDATE users SET
                            username = ?,
                            password_hash = ?,
                            created_at = ?,
                            updated_at = ?
                        WHERE id = ?
                    """
                    assert_user_types(user)
                    values = (user.username, user.password_hash, user.created_at, user.updated_at, user.id)
                    self._db.execute(sql, values)
                    self._db.commit()
                else:
                    self.insert(user)
            if isinstance(obj, Charge):
                charge: Charge = obj
                if self.exists(charge):
                    charge.updated_at = utc_now()
                    sql = f"""
                        UPDATE charges SET
                            {self._charge_columns_for_update()}
                        WHERE uid = ?
                    """
                    assert_charge_types(charge)
                    values = self._charge_values_for_update(charge)
                    self._db.execute(sql, values)
                    self._db.commit()
                else:
                    self.insert(charge)
            if isinstance(obj, DummyStoreOrder):
                order: DummyStoreOrder = obj
                if self.exists(order):
                    sql = f"""
                        UPDATE dummy_store_orders SET
                            {self._dummy_store_order_columns_for_update()}
                        WHERE uid = ?
                    """
                    values = self._dummy_store_order_values_for_update(order)
                    self._db.execute(sql, values)
                    self._db.commit()
                else:
                    self.insert(order)

    def exists(self, obj: [User, Charge, DummyStoreOrder]) -> bool:
        with self.lock:
            if isinstance(obj, User):
                user: User = obj
                if user.id:
                    sql = 'SELECT COUNT(*) FROM users WHERE id = ?'
                    values = [user.id]
                    ret = self._db.execute(sql, values)
                    return ret.fetchone()[0] == 1
            if isinstance(obj, Charge):
                charge: Charge = obj
                if charge.uid:
                    sql = 'SELECT COUNT(*) FROM charges WHERE uid = ?'
                    values = [charge.uid]
                    ret = self._db.execute(sql, values)
                    return ret.fetchone()[0] == 1
            if isinstance(obj, DummyStoreOrder):
                order: DummyStoreOrder = obj
                if order.uid:
                    sql = 'SELECT COUNT(*) FROM dummy_store_orders WHERE uid = ?'
                    values = [order.uid]
                    ret = self._db.execute(sql, values)
                    return ret.fetchone()[0] == 1
            return False

    def reload(self, obj: [User, Charge]) -> [User, Charge]:
        with self.lock:
            if isinstance(obj, User):
                return self.get_user_by_id(obj.id, update_me=obj)
            if isinstance(obj, Charge):
                return self.get_charge_by_uid(obj.uid, update_me=obj)

    # -- Charges ------------------------------------------------------------------------------------------------------

    def get_charges_count(self) -> int:
        with self.lock:
            sql = 'SELECT COUNT(*) FROM charges'
            return self._db.execute(sql).fetchone()[0]

    def get_charges(self) -> List[Charge]:
        with self.lock:
            sql = f'SELECT {self.CHARGE_COLUMNS} FROM charges ORDER BY created_at'
            rows = self._db.execute(sql)
            charges = []
            for row in rows:
                charges.append(self.charge_from_row(row))
            return charges

    def get_charge_by_uid(self, uid, update_me: Charge = None) -> Charge:
        with self.lock:
            sql = f'SELECT {self.CHARGE_COLUMNS} FROM charges WHERE uid = ?'
            values = [uid]
            row = self._db.execute(sql, values).fetchone()
            if row:
                return self.charge_from_row(row, update_me)

    # TODO: to be removed; address derivation index should not rely on charges being in database
    def count_charges_where_wallet_fingerprint_is(self, wallet_fingerprint) -> int:
        with self.lock:
            sql = 'SELECT COUNT(*) FROM charges WHERE wallet_fingerprint = ?'
            values = [wallet_fingerprint]
            return self._db.execute(sql, values).fetchone()[0]

    def get_charges_by_status(self, expected_status) -> List[Charge]:
        with self.lock:
            sql = f'SELECT {self.CHARGE_COLUMNS} FROM charges WHERE status = ?'
            values = [expected_status]
            rows = self._db.execute(sql, values)
            charges = []
            for row in rows:
                charges.append(self.charge_from_row(row))
            return charges

    def get_recently_created_charges(self, delta: [datetime.timedelta, None] = None) -> List[Charge]:
        with self.lock:
            if delta is not None:
                after = utc_now() - delta
            else:
                after = datetime.datetime.min  # beginning of time
            sql = f'SELECT {self.CHARGE_COLUMNS} FROM charges WHERE created_at > ? ORDER BY created_at DESC'
            values = [after]
            rows = self._db.execute(sql, values)
            charges = []
            for row in rows:
                charges.append(self.charge_from_row(row))
            return charges

    def get_recently_activated_charges(self, delta: [datetime.timedelta, None] = None) -> List[Charge]:
        with self.lock:
            if delta is not None:
                after = utc_now() - delta
            else:
                after = datetime.datetime.min  # beginning of time
            sql = f'SELECT {self.CHARGE_COLUMNS} FROM charges WHERE status != ? AND activated_at > ? ORDER BY created_at DESC'
            values = ['draft', after]
            rows = self._db.execute(sql, values)
            charges = []
            for row in rows:
                charges.append(self.charge_from_row(row))
            return charges

    def get_last_charge(self) -> [Charge, None]:
        with self.lock:
            sql = f'SELECT {self.CHARGE_COLUMNS} FROM charges ORDER BY created_at DESC LIMIT 1'
            row = self._db.execute(sql).fetchone()
            if row:
                return self.charge_from_row(row)

    def get_charges_for_merchant_notification(self, statuses: List):
        placeholders = ','.join(['?' for _ in statuses])
        with self.lock:
            sql = f"""
                SELECT {self.CHARGE_COLUMNS} FROM charges
                WHERE
                    status IN ({placeholders}) AND
                    merchant_order_id IS NOT NULL AND
                    merchant_callback_url_called_at IS NULL
                ORDER BY completed_at, cancelled_at, expired_at
            """
            values = statuses
            rows = self._db.execute(sql, values)
            charges = []
            for row in rows:
                charges.append(self.charge_from_row(row))
            return charges

    def count_and_sum_charges_grouped_by_status(self, activated_after: datetime) -> Cursor:
        with self.lock:
            sql = f"""
                SELECT status, COUNT(uid), SUM(usd_total)
                FROM charges
                WHERE
                  activated_at IS NOT NULL AND
                  activated_at >= ?
                GROUP BY status
            """
            values = [activated_after]
            rows = self._db.execute(sql, values)
            return rows

    # -- Users --------------------------------------------------------------------------------------------------------

    def get_users_count(self) -> int:
        with self.lock:
            sql = 'SELECT COUNT(*) FROM users'
            return self._db.execute(sql).fetchone()[0]

    def get_users(self) -> List[User]:
        with self.lock:
            sql = f'SELECT {self.USER_COLUMNS} FROM users ORDER BY created_at'
            rows = self._db.execute(sql)
            users = []
            for row in rows:
                users.append(self.user_from_row(row))
            return users

    def get_user_by_id(self, user_id, update_me: User = None) -> [User, None]:
        with self.lock:
            sql = f'SELECT {self.USER_COLUMNS} FROM users WHERE username = ?'
            values = [user_id]
            row = self._db.execute(sql, values).fetchone()
            if row:
                return self.user_from_row(row, update_me)

    def get_user_by_username(self, username: str) -> [User, None]:
        with self.lock:
            sql = f'SELECT {self.USER_COLUMNS} FROM users WHERE username = ?'
            values = [username]
            row = self._db.execute(sql, values).fetchone()
            if row:
                return self.user_from_row(row)

    def delete_all_users(self) -> None:
        with self.lock:
            # noinspection SqlWithoutWhere
            sql = 'DELETE FROM users'
            self._db.execute(sql)
            self._db.commit()

    # -- Utils --------------------------------------------------------------------------------------------------------

    def get_blockchain_height(self, coin: str, cc_network: str) -> int:
        sql = 'SELECT blockchain_height FROM coins WHERE cc_currency = ? AND cc_network = ?'
        values = [coin.casefold(), cc_network.casefold()]
        ret = self._db.execute(sql, values)
        return int(ret.fetchone()[0])

    def update_blockchain_height(self, coin: str, cc_network: str, height: int):
        sql = 'UPDATE coins SET blockchain_height = ? WHERE cc_currency = ? AND cc_network = ?'
        values = [height, coin.casefold(), cc_network.casefold()]
        self._db.execute(sql, values)
        self._db.commit()

    def get_admin_unique_path_segment(self) -> str:
        with self.lock:
            sql = f'SELECT {self.GLOBALS_COLUMNS} FROM globals WHERE key = ?'
            values = ['admin_unique_path_segment']
            row = self._db.execute(sql, values).fetchone()
            if row:
                return row['value']

    def insert_admin_unique_path_segment(self, v) -> None:
        with self.lock:
            sql = f"""
                INSERT
                    INTO globals (key, value, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
            """
            now = utc_now()
            values = ('admin_unique_path_segment', v, now, now)
            self._db.execute(sql, values)
            self._db.commit()

    def user_from_row(self, row, update_me=None) -> User:
        if update_me is None:
            user = User(username=row['username'], password_hash=row['password_hash'])
        else:
            user = update_me
            user.username = row['username']
            user.password_hash = row['password_hash']
        user.id = row['id']
        user.created_at = self.soft_apply_utc(row['created_at'])
        user.updated_at = self.soft_apply_utc(row['updated_at'])
        assert_user_types(user)
        return user

    def charge_from_row(self, row, update_me=None) -> Charge:
        if update_me is None:
            charge = Charge(
                total=db_int8_to_decimal(row['total']),
                currency=row['currency'],
                time_to_pay_ms=row['time_to_pay_ms'],
                time_to_complete_ms=row['time_to_complete_ms']
            )
        else:
            charge = update_me
            charge.total = db_int8_to_decimal(row['total'])
            charge.currency = row['currency']
            charge.time_to_pay_ms = row['time_to_pay_ms']
            charge.time_to_complete_ms = row['time_to_complete_ms']

        charge.uid = row['uid']
        charge.merchant_order_id = row['merchant_order_id']

        charge.cc_total = db_int8_to_decimal(row['cc_total'])
        charge.cc_currency = row['cc_currency']
        charge.cc_address = row['cc_address']
        charge.cc_lightning_payment_request = row['cc_lightning_payment_request']
        charge.cc_price = db_int8_to_decimal(row['cc_price'])

        charge.usd_total = db_int8_to_decimal(row['usd_total'])

        charge.pay_status = row['pay_status']
        charge.status = row['status']
        charge.cc_received_total = db_int8_to_decimal(row['cc_received_total'])
        charge.confirmations = int(row['confirmations'])

        charge.activated_at = self.soft_apply_utc(row['activated_at'])
        charge.paid_at = self.soft_apply_utc(row['paid_at'])
        charge.completed_at = self.soft_apply_utc(row['completed_at'])
        charge.expired_at = self.soft_apply_utc(row['expired_at'])
        charge.cancelled_at = self.soft_apply_utc(row['cancelled_at'])
        charge.merchant_callback_url_called_at = self.soft_apply_utc(row['merchant_callback_url_called_at'])

        charge.wallet_fingerprint = row['wallet_fingerprint']
        charge.address_derivation_index = row['address_derivation_index']

        charge.beneficiary = row['beneficiary']
        charge.what_for = row['what_for']
        charge.status_fixed_manually = bool(row['status_fixed_manually'])

        charge.block_explorer_1 = row['block_explorer_1']
        charge.block_explorer_2 = row['block_explorer_2']
        charge.subsequent_discrepancies = int(row['subsequent_discrepancies'])


        charge.created_at = self.soft_apply_utc(row['created_at'])
        charge.updated_at = self.soft_apply_utc(row['updated_at'])

        assert_charge_types(charge)
        return charge

    def dummystore_order_from_row(self, row) -> DummyStoreOrder:
        order = DummyStoreOrder(
            uid=row['uid'],
            item_id=row['item_id'],
            total=db_int8_to_decimal(row['total']),
            currency=row['currency'],
        )
        order.cc_total = db_int8_to_decimal(row['cc_total'])
        order.cc_currency = row['cc_currency']
        return order

    GLOBALS_COLUMNS = 'id, key, value, created_at, updated_at'

    USER_COLUMNS = 'id, username, password_hash, created_at, updated_at'

    CHARGE_COLUMNS = """
                uid,

                time_to_pay_ms,
                time_to_complete_ms,
                merchant_order_id,

                total,
                currency,

                cc_total,
                cc_currency,
                cc_address,
                cc_lightning_payment_request,
                cc_price,

                usd_total,

                pay_status,
                status,
                cc_received_total,
                confirmations,

                activated_at,
                paid_at,
                completed_at,
                expired_at,
                cancelled_at,
                merchant_callback_url_called_at,

                wallet_fingerprint,
                address_derivation_index,

                beneficiary,
                what_for,
                status_fixed_manually,

                block_explorer_1,
                block_explorer_2,
                subsequent_discrepancies,

                created_at,
                updated_at
    """

    DUMMY_STORE_ORDERS_COLUMNS = 'uid, item_id, total, currency, cc_total, cc_currency'

    def _charge_values(self, charge):
        return [
            charge.uid,

            int(charge.time_to_pay_ms),
            int(charge.time_to_complete_ms),
            charge.merchant_order_id,

            decimal_to_db_int8(charge.total),
            charge.currency,

            decimal_to_db_int8(charge.cc_total),
            charge.cc_currency,
            charge.cc_address,
            charge.cc_lightning_payment_request,
            decimal_to_db_int8(charge.cc_price),

            decimal_to_db_int8(charge.usd_total),

            charge.pay_status,
            charge.status,
            decimal_to_db_int8(charge.cc_received_total),
            int(charge.confirmations),

            charge.activated_at,
            charge.paid_at,
            charge.completed_at,
            charge.expired_at,
            charge.cancelled_at,
            charge.merchant_callback_url_called_at,

            charge.wallet_fingerprint,
            int(charge.address_derivation_index) if charge.address_derivation_index else None,

            charge.beneficiary,
            charge.what_for,
            charge.status_fixed_manually,

            charge.block_explorer_1,
            charge.block_explorer_2,
            int(charge.subsequent_discrepancies),

            charge.created_at,
            charge.updated_at
        ]

    def _charge_columns_for_update(self):
        return self.CHARGE_COLUMNS.replace('uid,', '') .replace(',', ' = ?,').replace('updated_at', 'updated_at = ?')

    def _charge_values_for_update(self, charge: Charge):
        return self._charge_values(charge)[1:] + [charge.uid]

    def _dummy_store_order_values(self, order: DummyStoreOrder):
        return [
            order.uid,
            order.item_id,
            decimal_to_db_int8(order.total),
            order.currency,
            decimal_to_db_int8(order.cc_total),
            order.cc_currency
        ]

    def _dummy_store_order_columns_for_update(self):
        return self.DUMMY_STORE_ORDERS_COLUMNS.replace('uid,', '') .replace(',', ' = ?,').replace('cc_currency', 'cc_currency = ?')

    def _dummy_store_order_values_for_update(self, order: DummyStoreOrder):
        return self._dummy_store_order_values(order)[1:] + [order.uid]

    def get_order_by_uid(self, uid: str) -> DummyStoreOrder:
        with self.lock:
            sql = f'SELECT {self.DUMMY_STORE_ORDERS_COLUMNS} FROM dummy_store_orders WHERE uid = ?'
            values = [uid]
            row = self._db.execute(sql, values).fetchone()
            if row:
                return self.dummystore_order_from_row(row)

    def get_orders(self) -> List[DummyStoreOrder]:
        with self.lock:
            sql = f'SELECT {self.DUMMY_STORE_ORDERS_COLUMNS} FROM dummy_store_orders ORDER BY uid'
            rows = self._db.execute(sql)
            orders = []
            for row in rows:
                orders.append(self.dummystore_order_from_row(row))
            return orders

    @staticmethod
    def soft_apply_utc(dt: datetime.datetime):
        if dt:
            return dt.replace(tzinfo=timezone.utc)
        else:
            return dt


def decimal_to_db_int8(amount: [Decimal, int, None]) -> [int, None]:
    """ Converts decimal amount to 8-byte integer for sqlite3.
        Assumes 8 significant decimal digits.
    """
    if amount is None:
        return None
    if isinstance(amount, int):
        amount = Decimal(amount)
    return int((amount * 10**8).to_integral_value())


def db_int8_to_decimal(amount: [int, None]) -> [Decimal, None]:
    """ Converts integer amount to Decimal.
        Assumes 8 least significant integer digits are decimal digits.
    """
    if amount is None:
        return None
    return Decimal(amount) / 10**8
