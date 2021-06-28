import decimal
import json
import logging as log
from json.decoder import JSONDecodeError
from urllib.parse import urljoin

from cypherpunkpay.net.http_client.clear_http_client import ClearHttpClient


class LndClient(object):

    def __init__(self, service_url, macaroon, http_client=None):
        self.__service_url = service_url
        self.__macaroon = macaroon
        self.__http_client = http_client if http_client else ClearHttpClient()

    # Returns payment request string
    def addinvoice(self, total: decimal) -> str:
        url = urljoin(self.__service_url, 'v1/invoices')

        headers_d = {
            'Grpc-Metadata-macaroon': self.__macaroon
        }

        body_s = json.dumps({
            'memo': 'I AM MEMO FIELD',
            'value': str(round(total * 10**8)),
            'private': True
        })

        log.info(f'url={url}')
        log.info(f'headers={headers_d}')
        log.info(f'body={body_s}')
        res = self.__http_client.post_accepting_linkability(url, headers=headers_d, body=body_s, set_tor_browser_headers=False, verify=False)
        try:
            res_json = json.loads(res.text)
        except JSONDecodeError as e:
            log.error(f'Error calling LND: {res.text}')
            raise e

        return res_json['payment_request']
