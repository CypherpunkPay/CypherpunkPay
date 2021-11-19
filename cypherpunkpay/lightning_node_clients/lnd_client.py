from urllib.parse import urljoin

import requests

from cypherpunkpay.common import *

from cypherpunkpay import disable_unverified_certificate_warnings
from cypherpunkpay.bitcoin.ln_invoice import LnInvoice
from cypherpunkpay.net.http_client.clear_http_client import ClearHttpClient


class LightningException(Exception):
    pass


class InvalidMacaroonLightningException(LightningException):
    pass


class UnknownInvoiceLightningException(LightningException):
    pass


class LndClient(object):

    def __init__(self, lnd_node_url, invoice_macaroon=None, http_client=None):
        self._lnd_node_url = lnd_node_url
        self._invoice_macaroon = invoice_macaroon
        self._http_client = http_client if http_client else ClearHttpClient()

    # Returns payment request string
    def addinvoice(self, total_btc: [Decimal, None] = None, memo: str = None, expiry_seconds: [int, None] = None) -> str:
        # URL
        lnd_node_url = urljoin(self._lnd_node_url, 'v1/invoices')

        # Headers
        headers_d = self._auth_header()

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
            log.debug(f'Calling LND REST API: POST {lnd_node_url} with body={body_s}')
            disable_unverified_certificate_warnings()
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

        code = res_json.get('code')
        if code and code > 0:
            # We assume 'message' property is always returned in JSON response
            message = res_json['message']
            log.error(f'LND returned error code={code} with message [{message}]')
            if 'signature mismatch' in message:
                log.error(f'Error authenticating to LND, check btc_lightning_lnd_invoice_macaroon option in your cypherpunkpay.conf file')
                raise InvalidMacaroonLightningException()
            raise LightningException()

        return res_json['payment_request']

    def lookupinvoice(self, r_hash: bytes) -> LnInvoice:
        # Sanity check
        assert isinstance(r_hash, bytes)
        assert len(r_hash) == 32

        # URL
        lnd_node_url = urljoin(self._lnd_node_url, f'v1/invoice/{r_hash.hex()}')

        # Headers
        headers_d = self._auth_header()

        try:
            log.debug(f'Calling LND REST API: GET {lnd_node_url}')
            disable_unverified_certificate_warnings()
            res = self._http_get(headers_d, lnd_node_url)
        except requests.exceptions.RequestException as e:
            log.error(f'Error connecting to LND: {e}')
            raise LightningException()

        try:
            res_json = json.loads(res.text)
        except JSONDecodeError as e:
            log.error(f'Non-json response from LND: {res.text}')
            raise LightningException()

        code = res_json.get('code')
        if code and code > 0:
            # We assume 'message' property is always returned in JSON response
            message = res_json['message']
            log.error(f'LND returned error code={code} with message [{message}]')
            if code in [2, 5]:
                raise UnknownInvoiceLightningException()
            raise LightningException()

        ln_invoice = LnInvoice()

        if res_json['settled']:
            ln_invoice.is_settled = True
            ln_invoice.amt_paid_msat = int(res_json['amt_paid_msat'])

        return ln_invoice

    # private

    def _auth_header(self):
        if self._invoice_macaroon:
            return {'Grpc-Metadata-macaroon': self._invoice_macaroon}
        else:
            return {}

    #  mock me
    def _http_get(self, headers_d, lnd_node_url) -> requests.Response:
        return self._http_client.get_accepting_linkability(
            url=lnd_node_url,
            headers=headers_d,
            set_tor_browser_headers=False,
            verify=False
        )
