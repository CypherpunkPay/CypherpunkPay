import requests

from cypherpunkpay.common import *
from cypherpunkpay.net.tor_client.base_tor_circuits import BaseTorCircuits


class BaseHttpClient(object):

    DEFAULT_TIMEOUT = 32  # seconds

    # Note that "br" compression is not supported because it requires additional dependency:
    # https://github.com/google/brotli
    # Hence we only list 'gzip, deflate'

    TOR_BROWSER_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers'
    }

    def get(self, url, privacy_context) -> requests.Response:
        raise NotImplementedError()

    def post(self, url, privacy_context, headers: dict = None, body: str = None, set_tor_browser_headers: bool = True) -> requests.Response:
        raise NotImplementedError()

    def get_accepting_linkability(self, url: str) -> requests.Response:
        return self.get(url, privacy_context=BaseTorCircuits.SHARED_CIRCUIT_ID)

    def post_accepting_linkability(self, url: str, headers: dict = None, body: str = None, set_tor_browser_headers: bool = True) -> requests.Response:
        return self.post(url, privacy_context=BaseTorCircuits.SHARED_CIRCUIT_ID, headers=headers, body=body, set_tor_browser_headers=set_tor_browser_headers)

    def get_text_or_None_on_error(self, url: str, privacy_context: str) -> [str, None]:
        try:
            response = self.get(url=url, privacy_context=privacy_context)
            if response.ok:
                return response.text
            log.debug(f'HTTP response not OK, status_code={response.status_code}, text={response.text}')
        except requests.exceptions.RequestException as e:
            log.debug(f'HTTP request exception={e.__class__.__name__}')

    def post_return_text_or_None_on_error(self, url, privacy_context, headers: dict = None, body: str = None, set_tor_browser_headers: bool = True) -> [str, None]:
        try:
            response = self.post(url, privacy_context, headers, body, set_tor_browser_headers)
            if response.ok:
                return response.text
            log.debug(f'HTTP response not OK, status_code={response.status_code}, text={response.text}')
        except requests.exceptions.RequestException as e:
            log.debug(f'HTTP request exception={e.__class__.__name__}')

    def get_text_or_None_on_error_while_accepting_linkability(self, url: str) -> [str, None]:
        return self.get_text_or_None_on_error(url, privacy_context=BaseTorCircuits.SHARED_CIRCUIT_ID)

    def post_return_text_or_None_on_error_while_accepting_linkability(self, url, headers: dict = None, body: str = None, set_tor_browser_headers: bool = True) -> [str, None]:
        return self.post_return_text_or_None_on_error(url, BaseTorCircuits.SHARED_CIRCUIT_ID, headers, body, set_tor_browser_headers)
