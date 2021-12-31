import datetime
from decimal import Decimal

from cypherpunkpay.models.charge import Charge
from cypherpunkpay.models.user import User

# SQLite3 does not offer strong typing. We do want to make sure the types are exactly what we expect.
# Hence, manual type assertions for Python objects that are subject to db CRUD.


def assert_bool(value):
    assert isinstance(value, bool)


def assert_int(value):
    assert isinstance(value, int)


def assert_int_or_null(value):
    assert isinstance(value, int) or value is None


def assert_str(value):
    assert isinstance(value, str)


def assert_str_or_null(value):
    assert isinstance(value, str) or value is None


def assert_utc(value):
    assert isinstance(value, datetime.datetime)
    assert value.tzname() == 'UTC'


def assert_utc_or_null(value):
    if value is None: return
    assert isinstance(value, datetime.datetime)
    assert value.tzname() == 'UTC'


def assert_decimal(value):
    assert isinstance(value, Decimal)


def assert_decimal_or_null(value):
    assert isinstance(value, Decimal) or value is None


def assert_user_types(u: User):
    assert_str(u.username)
    assert_str(u.password_hash)
    assert_utc(u.created_at)
    assert_utc(u.updated_at)


def assert_charge_types(c: Charge):
    assert_str(c.uid)

    assert_int(c.time_to_pay_ms)
    assert_int(c.time_to_complete_ms)
    assert_str_or_null(c.merchant_order_id)

    assert_decimal(c.total)
    assert_str(c.currency)

    assert_decimal_or_null(c.cc_total)
    assert_str_or_null(c.cc_currency)
    assert_str_or_null(c.cc_address)
    assert_decimal_or_null(c.cc_price)

    assert_decimal_or_null(c.usd_total)

    assert_str(c.pay_status)
    assert_str(c.status)
    assert_decimal(c.cc_received_total)
    assert_int(c.confirmations)

    assert_utc_or_null(c.activated_at)
    assert_utc_or_null(c.paid_at)
    assert_utc_or_null(c.completed_at)
    assert_utc_or_null(c.expired_at)
    assert_utc_or_null(c.cancelled_at)
    assert_utc_or_null(c.merchant_callback_url_called_at)

    assert_str_or_null(c.wallet_fingerprint)
    assert_int_or_null(c.address_derivation_index)

    assert_bool(c.status_fixed_manually)

    assert_str_or_null(c.block_explorer_1)
    assert_str_or_null(c.block_explorer_2)
    assert_int(c.subsequent_discrepancies)

    assert_utc(c.created_at)
    assert_utc(c.updated_at)
