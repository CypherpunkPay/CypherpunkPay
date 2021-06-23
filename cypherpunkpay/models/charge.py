import base64
import io

import pyqrcode
import sha3

from cypherpunkpay.bitcoin import Bip32
from cypherpunkpay.common import *
from cypherpunkpay.config.config import Config
from cypherpunkpay.tools.cryptocurrency_payment_uri import CryptocurrencyPaymentUri
from cypherpunkpay.tools.safe_uid import SafeUid


class Charge:

    # metadata
    uid: str
    time_to_pay_ms: int
    time_to_complete_ms: int
    merchant_order_id: [str, None] = None

    # expected payment
    total: Decimal
    currency: str

    # expressed in cryptocurrency
    cc_total: [Decimal, None] = None
    cc_currency: [str, None] = None
    cc_address: [str, None] = None
    cc_price: [Decimal, None] = None

    # expressed in USD for statistics purposes (transacted USD equivalent to be known regardless of specific coin and fiat selected)
    usd_total: [Decimal, None] = None

    # progress
    pay_status: str = 'unpaid'               # track incoming payments
    status: str = 'draft'                    # track charge business status based on pay_status, high level business rules and manual overrides
    cc_received_total: Decimal = Decimal(0)
    confirmations: int = 0

    # progress timestamps
    activated_at: [datetime, None] = None    # when user picked cryptocurrency so cc amount can be calculated based on current prices
    paid_at: [datetime, None] = None         # when we learned about the latest tx
    completed_at: [datetime, None] = None    # when status set to completed (meaning, enough confirmations or manual completion)
    expired_at: [datetime, None] = None      # when expired to pay or expired to complete or manual expiration
    cancelled_at: [datetime, None] = None    # when manually cancelled
    payment_completed_url_called_at: [datetime, None] = None  # when merchant `payment_completed_notification_url` got successfully called

    # context
    wallet_fingerprint: [str, None] = None
    address_derivation_index: [int, None] = None

    # merchant tags
    status_fixed_manually: bool = False

    # fixed block explorers
    block_explorer_1: str = None
    block_explorer_2: str = None
    subsequent_discrepancies: int = 0        # if too many discrepancies, block explorers will be randomly picked again

    # technical
    created_at: datetime                     # set in constructor
    updated_at: datetime                     # set in constructor

    # dictionaries related to business status
    NON_FINAL = {'draft', 'awaiting'}
    ACTIVE = {'awaiting'}
    FINAL = {'completed', 'cancelled', 'expired'}

    TIME_TO_PAY_EDGE_TOLERANCE_MS = 2 * 60 * 1000  # 2 minutes

    def __init__(self,
                 total: Decimal,
                 currency: str,
                 time_to_pay_ms: int,
                 time_to_complete_ms: int,
                 qr_cache=None,
                 merchant_order_id: [str, None] = None
        ):
        self.uid = SafeUid.gen()
        self.created_at = utc_now()
        self.updated_at = self.created_at
        self.time_to_pay_ms = time_to_pay_ms
        self.time_to_complete_ms = time_to_complete_ms
        self.merchant_order_id = merchant_order_id

        self.total = total
        self.currency = currency.casefold()

        self._qr_cache = qr_cache if qr_cache else {}

    def payment_uri(self) -> str:
        return CryptocurrencyPaymentUri.get(self.cc_currency, self.cc_address, amount=self.cc_remaining_total())

    def qr_code(self):
        qrcode = pyqrcode.create(self.payment_uri(), error='L')
        buffer = io.BytesIO()
        qrcode.png(buffer, scale=8)
        return buffer.getvalue()

    def qr_code_base64(self) -> str:
        return base64.standard_b64encode(self.qr_code()).decode('ascii')

    def cached_qr_code_base64(self) -> str:
        key = self.payment_uri()
        if key not in self._qr_cache:
            self._qr_cache[key] = self.qr_code_base64()
        return self._qr_cache[key]

    def soft_time_to_pay(self) -> timedelta:
        return timedelta(milliseconds=self.time_to_pay_ms)

    def time_to_complete(self) -> timedelta:
        return timedelta(milliseconds=self.time_to_complete_ms)

    def soft_time_left_to_pay(self) -> timedelta:
        time_passed = (utc_now() - self.activated_at)
        time_left = max(self.soft_time_to_pay() - time_passed, timedelta(seconds=0))
        return time_left

    def time_left_to_pay(self) -> timedelta:
        internal_max_time = timedelta(milliseconds=self.time_to_pay_ms + self.TIME_TO_PAY_EDGE_TOLERANCE_MS)
        time_passed = (utc_now() - self.activated_at)
        time_left = max(internal_max_time - time_passed, timedelta(seconds=0))
        return time_left

    def time_left_to_complete(self) -> timedelta:
        time_passed = (utc_now() - self.activated_at)
        time_left = max(self.time_to_complete() - time_passed, timedelta(seconds=0))
        return time_left

    def paid_after_expiry(self):
        if self.paid_at is None:
            return False
        internal_max_time = timedelta(milliseconds=self.time_to_pay_ms + self.TIME_TO_PAY_EDGE_TOLERANCE_MS)
        time_passed = (self.paid_at - self.activated_at)
        return time_passed > internal_max_time

    def soft_time_left_to_pay_formatted(self):
        return "%d:%0.2d" % divmod(self.soft_time_left_to_pay().seconds, 60)

    def promile_of_soft_time_left_to_pay(self):
        return int(1000 * self.soft_time_left_to_pay().seconds*1000 / self.time_to_pay_ms)

    def is_soft_expired_to_pay(self):
        return not self.is_draft() and self.pay_status in {'unpaid', 'underpaid'} and self.soft_time_left_to_pay().total_seconds() < 1

    def is_hard_expired_to_pay(self):
        return not self.is_draft() and self.pay_status in {'unpaid', 'underpaid'} and self.time_left_to_pay().total_seconds() < 1

    def is_expired_to_complete(self):
        return not self.is_draft() and self.has_non_final_status() and self.time_left_to_complete().total_seconds() < 1

    def is_expired_to_complete__unpaid(self):
        return self.status in {'draft', 'awaiting'} and self.pay_status == 'unpaid' and self.time_left_to_complete().total_seconds() < 1

    def is_expired_to_complete__paid(self):
        return self.status in {'draft', 'awaiting'} and self.pay_status != 'unpaid' and self.time_left_to_complete().total_seconds() < 1

    def has_non_final_status(self):
        return self.status in self.NON_FINAL

    def has_final_status(self):
        return self.status in self.FINAL

    def is_draft(self):
        return self.status == 'draft'

    def is_awaiting(self):
        return self.status == 'awaiting'

    def is_completed(self):
        return self.status == 'completed'

    def is_expired(self):
        return self.status == 'expired'

    def is_cancelled(self):
        return self.status == 'cancelled'

    def is_active(self):
        return self.status in self.ACTIVE

    def is_unpaid(self):
        return self.pay_status == 'unpaid'

    def is_underpaid(self):
        return self.pay_status == 'underpaid'

    def is_paid(self):
        return self.pay_status == 'paid'

    def is_confirmed(self):
        return self.pay_status == 'confirmed'

    def cc_remaining_total(self) -> Decimal:
        return max(self.cc_total - self.cc_received_total, Decimal(0))

    def cc_overpaid_total(self):
        return max(self.cc_received_total - self.cc_total, Decimal(0))

    def is_overpaid(self):
        return self.cc_total and self.cc_overpaid_total() > 0

    def is_fiat(self):
        return self.currency in Config.supported_fiats()

    def is_donation(self):
        return self.merchant_order_id is None

    def received_total_converted_to_fiat(self):
        assert self.is_fiat()
        assert not self.is_draft()  # drafts don't have cc_currency known
        return self.cc_received_total * self.cc_price

    def refresh_job_id(self):
        return f'refresh_charge_{self.short_uid()}'

    def short_uid(self):
        return self.uid[0:10]

    def advance_to_awaiting(self):
        assert self.is_draft() or self.is_awaiting()
        assert self.cc_address
        assert self.cc_total
        assert self.cc_currency
        if self.is_draft():
            log.info(f'Charge {self.short_uid()} status {self.status} -> awaiting')
            self.activated_at = utc_now()
        self.status = 'awaiting'

    def advance_to_completed(self):
        log.info(f'Charge {self.short_uid()} status {self.status} -> completed')
        self.completed_at = utc_now()
        self.status = 'completed'

    def advance_to_expired(self):
        log.info(f'Charge {self.short_uid()} status {self.status} -> expired')
        self.expired_at = utc_now()
        self.status = 'expired'

    # if changed the charge UI needs to refresh / think UI cache invalidation
    def state_hash_for_ui(self):
        state = f'{self.pay_status} {self.status} {self.cc_received_total} {self.confirmations}'
        return sha3.sha3_256(state.encode('utf8')).hexdigest()

    def block_explorer_url(self):
        if self.cc_currency == 'btc':
            from cypherpunkpay import App
            if App().config().btc_mainnet():
                return f'https://blockstream.info/address/{self.cc_address}'
            else:
                return f'https://blockstream.info/testnet/address/{self.cc_address}'


class ExampleCharge:

    @staticmethod
    def create(
            uid=None,
            total=Decimal(1),
            currency='btc',
            cc_address='bc1q9uu4j9xgkppqx3g28ph30zrjte8fs7jaz79uf3',
            cc_total=None,
            cc_currency=None,
            timeout_ms=15*60*1000,
            timeout_to_complete_ms=24*60*60*1000,
            wallet_fingerprint=Bip32.wallet_fingerprint("zpub6oMKbeQTqZyz7mbfjdSBXbHwyXYYwEN5sDSV48rLqRk6rnLELQCnnG1GqKju3DwjKX7C8MkfTWjLUPCM6RoCMnTskbvQqaDSaatwVtBQVPL"),
            address_derivation_index=0,
            pay_status='unpaid',
            status='awaiting',
            created_at=None,
            activated_at=None,
            paid_at=None,
            cc_received_total=Decimal(0),
            merchant_order_id=None,
            subsequent_discrepancies=0,
        ):
        total = Decimal(total)
        cc_received_total = Decimal(cc_received_total)
        from cypherpunkpay.prices.price_tickers import ExamplePriceTickers
        if cc_total is None and status != 'draft':
            if cc_currency is None:
                cc_currency = 'btc'
            if currency in ['btc', 'xmr']:
                cc_price = 1
            else:  # assume fiat
                cc_price = ExamplePriceTickers().price(cc_currency, currency)
            cc_total = round(total / cc_price, 8)
        if cc_total:
            cc_total = Decimal(cc_total)
        usd_total = None
        if cc_currency and status != 'draft':
            cc_usd_price = ExamplePriceTickers().usd_price(cc_currency)
            usd_total = round(cc_total * cc_usd_price, 2)
        # https://iancoleman.io/bip39/
        # seed: off elite mango quick ramp angry useless neglect eternal file anchor ceiling negative grass artefact
        charge = Charge(
            total=total,
            currency=currency,
            time_to_pay_ms=timeout_ms,
            time_to_complete_ms=timeout_to_complete_ms,
            qr_cache={},
            merchant_order_id=merchant_order_id
        )
        charge.cc_total = cc_total
        charge.cc_currency = cc_currency
        charge.usd_total = usd_total
        charge.wallet_fingerprint = wallet_fingerprint
        charge.address_derivation_index = address_derivation_index
        charge.cc_address = cc_address
        charge.pay_status = pay_status
        charge.paid_at = paid_at
        charge.status = status
        charge.cc_received_total = cc_received_total
        charge.subsequent_discrepancies = subsequent_discrepancies
        if uid:
            charge.uid = uid
        if created_at:
            charge.created_at = created_at
        if status != 'draft':
            charge.activated_at = activated_at or charge.created_at
        return charge

    @classmethod
    def db_create(cls, db, **kwargs):
        charge = cls.create(**kwargs)
        db.insert(charge)
        return charge
