from cypherpunkpay.app import App
from cypherpunkpay.common import *
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.models.charge import Charge
from cypherpunkpay.models.credit import Credit
from cypherpunkpay.usecases import UseCase
from cypherpunkpay.usecases.ensure_block_explorers_uc import EnsureBlockExplorersUC
from cypherpunkpay.usecases.fetch_address_credits_from_explorers_uc import FetchAddressCreditsFromExplorersUC
from cypherpunkpay.usecases.fetch_address_credits_from_full_node_uc import FetchAddressCreditsFromFullNodeUC
from cypherpunkpay.usecases.fetch_credits_from_lightning_node_uc import FetchCreditsFromLightningNodeUC


class RefreshChargeUC(UseCase):

    charge_uid: str

    CONFIRMATIONS_TO_CONSIDER_COMPLETED = 2

    def __init__(self, charge_uid: str, current_height=None, db=None, http_client=None, config=None):
        self.charge_uid = charge_uid
        self._current_height = current_height
        self._db = db if db else App().db()
        self._config = config if config else App().config()
        self._http_client = http_client if http_client else App().http_client()

    def exec(self):
        charge: Charge = self._db.get_charge_by_uid(self.charge_uid)
        if charge.is_draft():
            return

        if self._current_height is None:
            cc_currency = charge.cc_currency
            cc_network = self._config.cc_network(charge.cc_currency)
            self._current_height = self._db.get_blockchain_height(cc_currency, cc_network)

        # methods helpers so no self is necessary
        total = self.total
        confirmations = self.confirmations

        if charge.is_hard_expired_to_pay() or charge.is_expired_to_complete():
            if not charge.has_final_status():
                charge.advance_to_expired()
            self._db.save(charge)
            if charge.is_lightning():
                # LN invoices can't be paid after expiry
                return
            # No return here. The charge may still have its *pay_status* updated.

        if charge.is_expired() and not charge.cc_total:
            # draft charge expired before user picked coin
            return

        if charge.is_cancelled() and not charge.cc_total:
            # charge got cancelled before user picked coin
            return

        if charge.is_lightning():
            if charge.is_expired() or charge.is_completed():
                # LN invoices that are expired or already paid cannot receive coins - no need to check
                return

        credits = self.fetch_credits(charge)  # This is many seconds!
        if credits is None:
            return  # fetching failed

        current_height = credits.blockchain_height()

        # Completed
        credits_confirmed_fully = credits.confirmed_n(self.CONFIRMATIONS_TO_CONSIDER_COMPLETED)
        total_confirmed_fully = total(credits_confirmed_fully)
        if total_confirmed_fully >= charge.cc_total:
            charge.cc_received_total = total_confirmed_fully
            charge.confirmations = confirmations(credits_confirmed_fully, current_height)
            charge.pay_status = 'confirmed'
            if charge.paid_at is None:
                # Possible when charge went directly from unpaid to completed
                charge.paid_at = utc_now()
            if not charge.has_final_status():
                charge.advance_to_completed()
            self._db.save(charge)
            return

        # Awaiting / confirmed
        credits_confirmed_1 = credits.confirmed_1()
        total_confirmed_1 = total(credits_confirmed_1)
        if total_confirmed_1 >= charge.cc_total:
            charge.cc_received_total = total_confirmed_1
            charge.confirmations = confirmations(credits_confirmed_1, current_height)
            charge.pay_status = 'confirmed'
            if charge.paid_at is None:
                # Possible when charge went directly from unpaid to completed
                charge.paid_at = utc_now()
            if not charge.has_final_status() and not charge.is_awaiting():
                charge.advance_to_awaiting()
            self._db.save(charge)
            return

        total_paid = total(credits.any())

        # Awaiting / paid
        if total_paid >= charge.cc_total:
            if charge.cc_received_total != total_paid:
                # does require update
                charge.cc_received_total = total_paid
                if charge.pay_status != 'paid':
                    charge.pay_status = 'paid'
                    charge.paid_at = utc_now()
                    charge.confirmations = 0
                if not charge.has_final_status() and not charge.is_awaiting():
                    charge.advance_to_awaiting()
                self._db.save(charge)
            return

        # Awaiting / underpaid
        if 0 < total_paid < charge.cc_total:
            if charge.cc_received_total != total_paid:
                # does require update
                charge.cc_received_total = total_paid
                charge.pay_status = 'underpaid'
                charge.confirmations = 0
                if not charge.has_final_status() and not charge.is_awaiting():
                    charge.advance_to_awaiting()
                self._db.save(charge)
            return

        # Awaiting / unpaid
        if total_paid == 0:
            if charge.cc_received_total != total_paid:
                # does require update to 0 (possible if tx disappeared from mempool)
                charge.cc_received_total = Decimal(0)
                charge.pay_status = 'unpaid'
                charge.confirmations = 0
                if not charge.has_final_status() and not charge.is_awaiting():
                    charge.advance_to_awaiting()
                self._db.save(charge)
            return

    def fetch_credits(self, charge) -> [AddressCredits, None]:
        if charge.is_lightning():
            return self.fetch_credits_from_lightning_node(charge)
        if self.full_node_enabled(charge):
            return self.fetch_address_credits_from_full_node(charge)
        else:
            self.ensure_valid_block_explorers(charge)
            credits = self.fetch_address_credits_from_explorers(charge)
            self._db.reload(charge)  # reload the charge - by now it could have been updated by other job
            if credits is None:
                # We couldn't determine address credits. Block explorer calls failed or there was a discrepancy among explorers.
                self.increment_subsequent_discrepancies(charge)
                return None
            self.reset_subsequent_discrepancies(charge)
            return credits

    def full_node_enabled(self, charge):
        if charge.cc_currency == 'btc':
            return self._config.btc_node_enabled()
        if charge.cc_currency == 'xmr':
            return self._config.xmr_node_enabled()

    def ensure_valid_block_explorers(self, charge):
        if charge.cc_currency == 'btc':
            did_change = EnsureBlockExplorersUC(charge, config=self._config).exec()
            if did_change:
                self._db.save(charge)
        if charge.cc_currency == 'xmr':
            pass  # XMR empty list of available block explorers cannot be used with EnsureBlockExplorer so we pass here

    # MOCK ME
    def fetch_credits_from_lightning_node(self, charge) -> [AddressCredits, None]:
        return FetchCreditsFromLightningNodeUC(
            cc_lightning_payment_request=charge.cc_lightning_payment_request,
            current_height=self._current_height,
            config=self._config,
            http_client=self._http_client
        ).exec()

    # MOCK ME
    def fetch_address_credits_from_full_node(self, charge) -> [AddressCredits, None]:
        return FetchAddressCreditsFromFullNodeUC(
            current_height=self._current_height,
            http_client=self._http_client
        ).exec()

    # MOCK ME
    def fetch_address_credits_from_explorers(self, charge) -> [AddressCredits, None]:
        return FetchAddressCreditsFromExplorersUC(
            charge.cc_currency,
            charge.cc_address,
            charge.block_explorer_1,
            charge.block_explorer_2,
            current_height=self._current_height,
            http_client=self._http_client,
            charge_short_uid=charge.short_uid()
        ).exec()

    def increment_subsequent_discrepancies(self, charge: Charge):
        charge.subsequent_discrepancies += 1
        log.info(f'Charge {charge.short_uid()} subsequent_discrepancies {charge.subsequent_discrepancies - 1} -> {charge.subsequent_discrepancies}')
        self._db.save(charge)

    def reset_subsequent_discrepancies(self, charge: Charge):
        if charge.subsequent_discrepancies > 0:
            log.info(f'Charge {charge.short_uid()} reset subsequent_discrepancies {charge.subsequent_discrepancies} -> 0')
            charge.subsequent_discrepancies = 0
            self._db.save(charge)

    def total(self, credits: List[Credit]):
        return sum(map(lambda c: c.value(), credits))

    def confirmations(self, credits: List[Credit], current_height):
        if credits:
            return min(map(lambda c: current_height - c.confirmed_height() + 1, credits))
        else:
            return 0
