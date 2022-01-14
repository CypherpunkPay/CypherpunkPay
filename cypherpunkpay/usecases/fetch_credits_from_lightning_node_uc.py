from cypherpunkpay.app import App
from cypherpunkpay.common import *
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.models.credit import Credit
from cypherpunkpay.usecases import UseCase
from cypherpunkpay.bitcoin import btc_network_class
from cypherpunkpay.lightning_node_clients.lnd_client import LndClient, LightningException
from cypherpunkpay.bitcoin.electrum.lnaddr import lndecode


class FetchCreditsFromLightningNodeUC(UseCase):

    def __init__(self, cc_lightning_payment_request: str, current_height: int, http_client=None, config=None):
        self.cc_lightning_payment_request = cc_lightning_payment_request
        self.current_height = current_height
        self.http_client = http_client if http_client else App().http_client()
        self.config = config if config else App().config()

    def exec(self) -> [AddressCredits, None]:
        lnd_client = self.instantiate_lnd_client()
        payment_request = lndecode(self.cc_lightning_payment_request, net=btc_network_class(self.config.btc_network()))
        try:
            ln_invoice = lnd_client.lookupinvoice(r_hash=payment_request.paymenthash)
        except LightningException:
            return None  # The exception has been logged upstream. The action will be retried. Safe to swallow.

        credits = []
        if ln_invoice.is_settled and ln_invoice.amt_paid_sat > 0:
            total_paid_btc = Decimal(ln_invoice.amt_paid_sat) / 10**8
            # Wrapped in AddressCredits for compatibility with existing charge resolution code.
            # Using huge/fake number of confirmations. In reality LN invoices do not have a concept of block confirmations.
            # Ideally LN charges should be dealt with separately w/o this hack.
            credit = Credit(total_paid_btc, self.current_height - 65535, has_replaceable_flag=False)
            credits.append(credit)
        return AddressCredits(credits, self.current_height)

    # MOCK ME
    def instantiate_lnd_client(self):
        return LndClient(
            lnd_node_url=self.config.btc_lightning_lnd_url(),
            invoice_macaroon=self.config.btc_lightning_lnd_invoice_macaroon(),
            http_client=self.http_client
        )
