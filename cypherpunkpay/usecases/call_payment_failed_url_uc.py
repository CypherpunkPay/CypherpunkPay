import logging as log

from cypherpunkpay.usecases.call_merchant_base_uc import CallMerchantBaseUC


class CallPaymentFailedUrlUC(CallMerchantBaseUC):

    def exec(self):
        if not self._config.merchant_enabled() or \
           not self._charge.merchant_order_id or \
           not (self._charge.is_cancelled() or self._charge.is_expired()):
            return

        log.debug(f'Notifying merchant on status={self._charge.status} for {self._charge.short_uid()}')

        url = self._config.payment_failed_notification_url()
        body = f"""
{{
  "untrusted": {{
    "merchant_order_id": "{self._charge.merchant_order_id}",
    "total": "{format(self._charge.total, 'f')}",
    "currency": "{self._charge.currency.casefold()}"
  }},
  "status": "{self._charge.status}"
}}""".strip()

        self.call_merchant_and_mark_as_done(url, body)
