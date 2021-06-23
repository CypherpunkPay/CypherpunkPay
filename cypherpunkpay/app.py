import logging as log
from typing import Dict

from cypherpunkpay.config.config import Config
from cypherpunkpay.db.db import DB
from cypherpunkpay.db.sqlite_db import SqliteDB
from cypherpunkpay.full_node_clients.bitcoin_core_client import BitcoinCoreClient
from cypherpunkpay.full_node_clients.json_rpc_client import JsonRpcError
from cypherpunkpay.jobs.job_adder import JobAdder
from cypherpunkpay.jobs.job_scheduler import JobScheduler

from cypherpunkpay.net.tor_client.base_tor_circuits import BaseTorCircuits
from cypherpunkpay.net.tor_client.official_tor_circuits import OfficialTorCircuits
from cypherpunkpay.net.http_client.base_http_client import BaseHttpClient
from cypherpunkpay.net.http_client.clear_http_client import ClearHttpClient
from cypherpunkpay.net.http_client.tor_http_client import TorHttpClient

from cypherpunkpay.prices.price_tickers import PriceTickers
from cypherpunkpay.tools.singleton import Singleton
from cypherpunkpay.tools.safe_uid import SafeUid


class App(object, metaclass=Singleton):

    _config: Config
    _db: [DB, None]
    _qr_cache: Dict[str, str]
    _tor_circuits: [BaseTorCircuits, None]
    _http_client: BaseHttpClient
    _price_tickers: PriceTickers
    _job_scheduler: [JobScheduler, None]

    def __init__(self, settings=None, config=None, job_scheduler=None, db=None, price_tickers=None):
        if settings is None:
            settings = {}
        self._silence_logging_for_dependencies()
        self._config = config if config else Config(settings)   # TODO: remove 'settings' param compatibility
        self._db = db if db else SqliteDB(self._config.db_file_path())
        self._db.connect()
        self._db.migrate()
        self._qr_cache = {}
        if self._config.use_tor():
            self._connect_tor()
            self._http_client = TorHttpClient(self._tor_circuits)
        else:
            self._tor_circuits = None
            self._http_client = ClearHttpClient()
        if self._config.btc_node_enabled() and 'btc' in self.config().configured_coins():
            self._connect_btc_node()
        self._price_tickers = price_tickers if price_tickers else PriceTickers(self._http_client)
        self._job_scheduler = job_scheduler if job_scheduler else JobScheduler()
        JobAdder(self).add_full_time_jobs()

    @staticmethod
    def _silence_logging_for_dependencies():
        log.getLogger('apscheduler').setLevel(log.CRITICAL)
        log.getLogger('apscheduler.scheduler').setLevel(log.CRITICAL)

    def _connect_tor(self):
        self._tor_circuits = OfficialTorCircuits(config=self._config)
        self._tor_circuits.connect_and_verify()

    def _connect_btc_node(self):
        try:
            BitcoinCoreClient(
                self.config().btc_node_rpc_url(),
                self.config().btc_node_rpc_user(),
                self.config().btc_node_rpc_password(),
                self.http_client()
            ).create_wallet_idempotent(self.config().btc_account_xpub())
        except JsonRpcError:
            pass  # The exception has been logged upstream. The action will be retried. Safe to swallow.

    def config(self) -> Config:
        return self._config

    def job_scheduler(self):
        return self._job_scheduler

    def tor_circuits(self):
        return self._tor_circuits

    def db(self) -> DB:
        return self._db

    def price_tickers(self):
        return self._price_tickers

    def http_client(self):
        return self._http_client

    def qr_cache(self):
        return self._qr_cache

    def current_blockchain_height(self, coin: str) -> int:
        return self.db().get_blockchain_height(coin, self._config.cc_network(coin))

    def get_admin_unique_path_segment(self) -> str:
        if self._config.prod_env():
            v = self._db.get_admin_unique_path_segment()
            if not v:
                v = SafeUid().gen(16)
                self._db.insert_admin_unique_path_segment(v)
            return v
        else:
            # fixed value for dev and test
            return 'eeec6kyl2rqhys72b6encxxrte'

    def close(self):
        log.info("Gracefully shutting down...")

        if self._job_scheduler:
            self._job_scheduler.shutdown()
            self._job_scheduler = None

        if self._tor_circuits:
            self._tor_circuits.close()
            self._tor_circuits = None

        if self._db:
            self._db.disconnect()
            self._db = None

    def is_fully_initialized(self):
        return self.price_tickers().is_fully_initialized()
