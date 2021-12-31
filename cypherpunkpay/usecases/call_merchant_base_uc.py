import logging as log
from abc import ABC

import requests
from requests import Response

from cypherpunkpay import utc_now
from cypherpunkpay.app import App
from cypherpunkpay.models.charge import Charge
from cypherpunkpay.net.tor_client.base_tor_circuits import BaseTorCircuits
from cypherpunkpay.usecases import UseCase


class CallMerchantBaseUC(UseCase, ABC):

    def __init__(self, charge: Charge, db=None, config=None, http_client=None):
        self._charge = charge
        self._db = db if db else App().db()
        self._config = config if config else App().config()
        self._http_client = http_client if http_client else App().http_client()

    def call_merchant_and_mark_as_done(self, url: str, body: str):
        if self._config.skip_tor_for_merchant_callbacks():
            privacy_context = BaseTorCircuits.SKIP_TOR
        else:
            privacy_context = BaseTorCircuits.SHARED_CIRCUIT_ID

        try:
            response: Response = self._http_client.post(url, privacy_context=privacy_context, headers=self.headers(), body=body)
        except requests.exceptions.RequestException as e:
            log.error(f'Calling merchant failed for {self._charge.short_uid()}, tried to POST {url} - got exception {e}')
            return

        if response.ok and not response.is_redirect:
            self._charge.merchant_callback_url_called_at = utc_now()
            self._db.save(self._charge)
            log.info(f'Calling merchant succeeded for {self._charge.short_uid()}')
        else:
            log.error(f'Calling merchant failed for {self._charge.short_uid()}, tried to POST {url} - got response with status code {response.status_code}')

    def headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self._config.cypherpunkpay_to_merchant_auth_token()}',
            'Content-Type': 'application/json'
        }
