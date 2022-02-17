from test.unit.test_case import *
from cypherpunkpay.db.sqlite_db import SqliteDB


class CypherpunkpayDBTestCase(CypherpunkpayTestCase):

    def setUp(self):
        super().setUp()
        self.db = SqliteDB(self.gen_tmp_file_path('.sqlite3'))
        self.db.connect()
        self.db.migrate()

    def tearDown(self):
        self.db.disconnect()
        super().tearDown()
