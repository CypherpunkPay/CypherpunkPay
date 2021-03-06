import requests

from cypherpunkpay.globals import *
from cypherpunkpay.tools.net import is_local_network, get_host_or_ip

from .base_http_client import BaseHttpClient
from ..tor_client.base_tor_circuits import BaseTorCircuits


class TorHttpClient(BaseHttpClient):

    _tor_circuits: BaseTorCircuits

    def __init__(self, tor_circuits: BaseTorCircuits = None):
        self._tor_circuits = tor_circuits

    def get(self, url: str, privacy_context: str, headers: dict = None, set_tor_browser_headers: bool = True, verify=None):
        if is_local_network(url):
            privacy_context = BaseTorCircuits.SKIP_TOR
        if privacy_context == BaseTorCircuits.SHARED_CIRCUIT_ID:
            privacy_context = get_host_or_ip(url)
        session = self._tor_circuits.get_for(privacy_context)
        try:
            if set_tor_browser_headers:
                combined_headers = {
                    **BaseHttpClient.TOR_BROWSER_HEADERS,
                    **(headers or {})
                }
            else:
                combined_headers = headers or {}
            res = session.get(url, headers=combined_headers, timeout=BaseHttpClient.DEFAULT_TIMEOUT, verify=verify)
            self.log_error_status_codes(res)
            return res
        except requests.exceptions.RequestException as e:
            self._tor_circuits.mark_as_broken(privacy_context)
            raise e

    def post(self, url: str, privacy_context: str, headers: dict = None, body: str = None, set_tor_browser_headers: bool = True, verify=None):
        if is_local_network(url):
            privacy_context = BaseTorCircuits.SKIP_TOR
        if privacy_context == BaseTorCircuits.SHARED_CIRCUIT_ID:
            privacy_context = get_host_or_ip(url)
        session = self._tor_circuits.get_for(privacy_context)
        if set_tor_browser_headers:
            combined_headers = {
                **BaseHttpClient.TOR_BROWSER_HEADERS,
                **(headers or {})
            }
        else:
            combined_headers = headers or {}
        body = body or {}
        try:
            res = session.post(url, headers=combined_headers, data=body, timeout=BaseHttpClient.DEFAULT_TIMEOUT, verify=verify)
            self.log_error_status_codes(res)
            return res
        except requests.exceptions.RequestException as e:
            self._tor_circuits.mark_as_broken(privacy_context)
            raise e
