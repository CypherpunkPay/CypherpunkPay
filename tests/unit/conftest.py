import pytest

from cypherpunkpay.db.sqlite_db import SqliteDB


@pytest.fixture(scope='session')
def database_migrated(tmp_path_factory):
    # SETUP
    from tests.unit.db_test_case import CypherpunkpayDBTestCase
    base_class = CypherpunkpayDBTestCase
    db_file_path = str(tmp_path_factory.mktemp('unit') / 'db.sqlite3')
    base_class.db = SqliteDB(db_file_path)
    base_class.db.connect()
    base_class.db.migrate()

    yield

    # TEARDOWN
    base_class.db.disconnect()


@pytest.fixture(scope='function')
def database_transaction():
    # SETUP
    from tests.unit.db_test_case import CypherpunkpayDBTestCase
    base_class = CypherpunkpayDBTestCase
    base_class.db.execute('BEGIN')

    yield

    # TEARDOWN
    base_class.db.execute('ROLLBACK')
