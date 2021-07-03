from cypherpunkpay.net.http_client.tor_http_client import BaseHttpClient


class DummyHttpClient(BaseHttpClient):

    def get(self, url, privacy_context, headers: dict = None, set_tor_browser_headers: bool = True, verify=None):
        pass

    def post(self, url, privacy_context, headers: dict = None, body: dict = None, set_tor_browser_headers: bool = True, verify=None):
        pass
