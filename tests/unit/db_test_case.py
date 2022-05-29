import pytest

from tests.unit.test_case import CypherpunkpayTestCase

from cypherpunkpay.db.sqlite_db import SqliteDB


@pytest.mark.usefixtures('database_migrated')
@pytest.mark.usefixtures('database_transaction')
class CypherpunkpayDBTestCase(CypherpunkpayTestCase):

    db: SqliteDB
