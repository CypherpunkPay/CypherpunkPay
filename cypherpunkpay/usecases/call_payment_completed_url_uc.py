import logging as log

import requests
from requests import Response

from cypherpunkpay import utc_now
from cypherpunkpay.app import App
from cypherpunkpay.models.charge import Charge
from cypherpunkpay.usecases import UseCase


class CallPaymentCompletedUrlUC(UseCase):

    def __init__(self, charge: Charge, db=None, config=None, http_client=None):
        self._charge = charge
        self._db = db if db else App().db()
        self._config = config if config else App().config()
        self._http_client = http_client if http_client else App().http_client()

    def exec(self):
        if not self._config.merchant_enabled() or \
           not self._charge.is_completed() or \
           not self._charge.merchant_order_id:
            return

        log.debug(f'Notifying merchant on completion of {self._charge.short_uid()}')

        url = self._config.payment_completed_notification_url()
        headers = {
            'Authorization': f'Bearer {self._config.cypherpunkpay_to_merchant_auth_token()}',
            'Content-Type': 'application/json'
        }
        body = f"""
{{
  "untrusted": {{
    "merchant_order_id": "{self._charge.merchant_order_id}",
    "total": "{format(self._charge.total, 'f')}",
    "currency": "{self._charge.currency.casefold()}"
  }},
  "status": "completed",
  "cc_total": "{format(self._charge.cc_total, 'f')}",
  "cc_currency": "{self._charge.cc_currency.casefold()}"
}}""".strip()
        try:
            response: Response = self._http_client.post_accepting_linkability(url, headers=headers, body=body)
        except requests.exceptions.RequestException as e:
            log.error(f'Calling marchant failed, tried to POST {url} - got exception {e}')
            return

        if response.ok and not response.is_redirect:
            self._charge.payment_completed_url_called_at = utc_now()
            self._db.save(self._charge)
