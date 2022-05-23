from typing import Optional

from tests.unit.test_case import *
from cypherpunkpay.db.sqlite_db import SqliteDB


class CypherpunkpayDBTestCase(CypherpunkpayTestCase):

    db: Optional[SqliteDB] = None

    @classmethod
    def setup_class(cls):
        cls.db = SqliteDB(CypherpunkpayTestCase.gen_tmp_file_path('.sqlite3'))
        cls.db.connect()
        cls.db.migrate()

    @classmethod
    def teardown_class(cls):
        cls.db.disconnect()
        cls.db = None  # make it more explicit

    def setup_method(self):
        super().setup_method()
        self.db._db.execute('BEGIN')

    def teardown_method(self):
        self.db._db.execute('ROLLBACK')
        super().teardown_method()
