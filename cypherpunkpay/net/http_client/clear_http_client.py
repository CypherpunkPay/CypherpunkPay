import requests

from cypherpunkpay.net.http_client.tor_http_client import BaseHttpClient


class ClearHttpClient(BaseHttpClient):

    def __init__(self, notused=None):
        self.session = requests.sessions.Session()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()

    def get(self, url, privacy_context):
        return self.session.get(url, headers=BaseHttpClient.TOR_BROWSER_HEADERS, timeout=BaseHttpClient.DEFAULT_TIMEOUT)

    def post(self, url, privacy_context, headers: dict = None, body: str = None, set_tor_browser_headers: bool = True):
        if set_tor_browser_headers:
            combined_headers = {
                **BaseHttpClient.TOR_BROWSER_HEADERS,
                **(headers or {})
            }
        else:
            combined_headers = headers or {}
        body = body or ''
        return self.session.post(url, headers=combined_headers, data=body, timeout=BaseHttpClient.DEFAULT_TIMEOUT)
