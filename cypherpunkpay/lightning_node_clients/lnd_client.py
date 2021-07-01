import decimal
import json
import logging as log
from json.decoder import JSONDecodeError
from urllib.parse import urljoin
from datetime import datetime

import requests

from cypherpunkpay import disable_unverified_certificat_warnings
from cypherpunkpay.net.http_client.clear_http_client import ClearHttpClient


class LightningException(Exception):
    pass


class LndClient(object):

    def __init__(self, lnd_node_url, invoice_macaroon=None, http_client=None):
        self._lnd_node_url = lnd_node_url
        self._invoice_macaroon = invoice_macaroon
        self._http_client = http_client if http_client else ClearHttpClient()

    # Returns payment request string
    def addinvoice(self, total_btc: [decimal, None] = None, memo: str = None, expiry_seconds: [int, None] = None) -> str:
        # URL
        lnd_node_url = urljoin(self._lnd_node_url, 'v1/invoices')

        # Headers
        if self._invoice_macaroon:
            headers_d = {'Grpc-Metadata-macaroon': self._invoice_macaroon}
        else:
            headers_d = {}

        # Body
        body_d = {'private': True}
        if memo:
            body_d['memo'] = memo
        if total_btc:
            total_satoshi = round(total_btc * 10 ** 8)
            body_d['value'] = str(total_satoshi)
        if expiry_seconds:
            body_d['expiry'] = str(expiry_seconds)
        body_s = json.dumps(body_d)

        try:
            log.debug(f'Calling LND REST API at {lnd_node_url} with body={body_s}')
            disable_unverified_certificat_warnings()
            res = self._http_client.post_accepting_linkability(
                url=lnd_node_url,
                headers=headers_d,
                body=body_s,
                set_tor_browser_headers=False,
                verify=False
            )
        except requests.exceptions.RequestException as e:
            log.error(f'Error connecting to LND: {e}')
            raise LightningException()

        try:
            res_json = json.loads(res.text)
        except JSONDecodeError as e:
            log.error(f'Non-json response from LND: {res.text}')
            raise LightningException()

        if 'error' in res_json:
            log.error(f'LND returned error: {res_json["error"]}')
            raise LightningException()

        return res_json['payment_request']
