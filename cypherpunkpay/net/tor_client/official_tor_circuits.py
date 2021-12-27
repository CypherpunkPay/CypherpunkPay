import logging as log
import sys
import threading
import time

import requests
from requests import Session

from cypherpunkpay.config.config import Config
from cypherpunkpay.net.tor_client.base_tor_circuits import BaseTorCircuits


class OfficialTorCircuits(BaseTorCircuits):

    _config: Config
    TARGET_CIRCUITS_POOL_SIZE = 32

    def __init__(self, config):
        self._config = config
        self._sessions = {}
        self._global_lock = threading.RLock()
        self._lock_for = {}  # never trimmed; will slowly leak memory

    # This must be called after constructor and before any other methods
    def connect_and_verify(self):
        with self._global_lock:
            self._verify_exiting_through_tor()

    def _verify_exiting_through_tor(self):
        log.info(f'Verifying connections actually go through Tor via SOCKS5 proxy {self._config.tor_socks5_host()}:{self._config.tor_socks5_port()}')
        try:
            res = self._check_torproject_org(attempts=4)
            if 'Congratulations' not in res.text:
                if 'You are not using Tor' in res.text:
                    log.error('Tor is not used according to check.torproject.org - exiting')
                    sys.exit(1)
                else:
                    log.warning('Cannot tell if Tor is being used. Update the software')
        except Exception as e:
            log.error(f'Connection through Tor daemon SOCKS5 proxy failed. Do you have `SocksPort` enabled in your torrc? Is your tor daemon running? Verify your config entries `tor_socks5_host`, `tor_socks5_port`. Error details: {e}')
            sys.exit(1)

    def _check_torproject_org(self, attempts):
        for attempt in range(attempts):
            try:
                session = self.get_for(BaseTorCircuits.SHARED_CIRCUIT_ID)
                return session.get('https://check.torproject.org/')
            except Exception as e:
                if attempt+1 < attempts:
                    log.warning(f'Retrying...')
                    time.sleep(attempt*2)  # sleep(0), sleep(2), sleep(4)
                else:
                    raise e

    # Use special label 'skip_tor' to avoid setting socks5 proxy
    def get_for(self, label: str) -> requests.Session:
        with self._global_lock:
            if label not in self._lock_for:
                self._lock_for[label] = threading.RLock()

        with self._lock_for[label]:
            session = self._sessions.get(label, None)
            if session is None:
                session = self._create_for(label)

        return session

    def _create_for(self, label):
        session = Session()
        if label != BaseTorCircuits.SKIP_TOR:
            socks5_proxy = f'socks5h://{label}:{label}@{self._config.tor_socks5_host()}:{self._config.tor_socks5_port()}'
            session.proxies = {'http': socks5_proxy, 'https': socks5_proxy}
        self._sessions[label] = session
        return session

    def close(self):
        with self._global_lock:
            for session in self._sessions.values():
                session.__exit__()
            self._sessions = {}

    def mark_as_broken(self, label):
        with self._lock_for[label]:
            if label not in self._sessions:
                return
            self._sessions.pop(label).close()
