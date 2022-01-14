from cypherpunkpay.bitcoin.ln_invoice import LnInvoice
from cypherpunkpay.common import *
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.models.charge import ExampleCharge, Charge
from cypherpunkpay.models.credit import Credit
from test.unit.db_test_case import CypherpunkpayDBTestCase
from cypherpunkpay.net.http_client.dummy_http_client import DummyHttpClient
from cypherpunkpay.usecases.refresh_charge_uc import RefreshChargeUC
from test.unit.config.example_config import ExampleConfig


class StubRefreshChargeUC(RefreshChargeUC):

    def __init__(self, charge_uid: str, credits: [List[Credit], None], blockchain_height=None, db=None):
        self._blockchain_height = blockchain_height or 2**31  # just big
        super().__init__(charge_uid, current_height=self._blockchain_height, db=db, http_client=DummyHttpClient(), config=ExampleConfig())
        self._mock_credits = credits

    def fetch_address_credits_from_explorers(self, charge):
        if self._mock_credits is None:
            return None
        else:
            return AddressCredits(self._mock_credits, self._blockchain_height)


class StubLnRefreshChargeUC(RefreshChargeUC):

    def __init__(self, charge_uid: str, credits: [List[Credit], None], db=None):
        self._blockchain_height = 2**31  # just big
        super().__init__(charge_uid, current_height=self._blockchain_height, db=db, http_client=DummyHttpClient(), config=ExampleConfig())
        self._mock_credits = credits

    def fetch_credits_from_lightning_node(self, charge) -> [AddressCredits, None]:
        return AddressCredits(self._mock_credits, self._blockchain_height)


class RefreshChargeUCTest(CypherpunkpayDBTestCase):

    def test_remain_awaiting_unpaid_when_no_credits(self):
        charge = ExampleCharge.db_create(self.db)
        uc = StubRefreshChargeUC(charge.uid, credits=[], db=self.db)
        uc.exec()
        self.assertTrue(charge.is_unpaid())
        self.assertTrue(charge.is_awaiting())

    def test_remain_awaiting_underpaid_when_None_credits(self):
        # Suddenly "None credits" for already paid charge *CAN* happen because of temporary discrepancy among block explorers. See FetchAddressCreditsUC.
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=900,
                                         status='awaiting',
                                         pay_status='underpaid')
        uc = StubRefreshChargeUC(charge.uid, credits=None, db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_awaiting())
        self.assertTrue(charge.is_underpaid())
        self.assertEqual(900, charge.cc_received_total)

    def test_increment_subsequent_discrepancies_when_None_credits(self):
        # "None credits" can happen because of temporary discrepancy among block explorers. See FetchAddressCreditsUC.
        charge = ExampleCharge.db_create(self.db)
        uc = StubRefreshChargeUC(charge.uid, credits=None, db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertEqual(1, charge.subsequent_discrepancies)

    def test_reset_subsequent_discrepancies_when_coherent_credits(self):
        charge = ExampleCharge.db_create(self.db)
        charge.subsequent_discrepancies = 3
        charge.block_explorer_1 = 'cypherpunkpay.explorers.bitcoin.blockstream_explorer BlockstreamExplorer'
        charge.block_explorer_2 = 'cypherpunkpay.explorers.bitcoin.trezor_explorer TrezorExplorer'
        self.db.save(charge)

        uc = StubRefreshChargeUC(charge.uid, [], db=self.db)
        uc.exec()
        self.db.reload(charge)

        self.assertEqual(0, charge.subsequent_discrepancies)

    # draft

    def test_draft_does_not_expire(self):
        minutes_60 = 60*60*1000
        charge = ExampleCharge.db_create(self.db,
                                         status='draft',
                                         timeout_to_complete_ms=minutes_60,
                                         created_at=utc_ago(minutes=61))
        uc = StubRefreshChargeUC(charge.uid, [], db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_unpaid())
        self.assertTrue(charge.is_draft())

    # awaiting: unpaid

    def test_unpaid_to_expired(self):
        minutes_15 = 15*60*1000
        charge = ExampleCharge.db_create(self.db,
                                         status='awaiting',
                                         pay_status='unpaid',
                                         timeout_ms=minutes_15,
                                         created_at=utc_ago(minutes=18))
        uc = StubRefreshChargeUC(charge.uid, [], db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_unpaid())
        self.assertTrue(charge.is_expired())

    def test_unpaid_to_underpaid(self):
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         status='awaiting',
                                         pay_status='unpaid')
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(900, 1), Credit.unconfirmed(99)], db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_underpaid())
        self.assertTrue(charge.is_awaiting())
        self.assertEqual(999, charge.cc_received_total)

    def test_unpaid_to_paid(self):
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         status='awaiting',
                                         pay_status='unpaid')
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(900, 1), Credit.confirmed(99, 1), Credit.unconfirmed(1)], db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_paid())
        self.assertTrue(charge.is_awaiting())
        self.assertEqual(1000, charge.cc_received_total)
        self.assertTrue(charge.paid_at)

    def test_unpaid_to_confirmed(self):
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         status='awaiting',
                                         pay_status='unpaid')
        height = 1
        current_height = 1
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(900, height - 1), Credit.confirmed(99, height), Credit.confirmed(1, height)], current_height, db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_confirmed())
        self.assertTrue(charge.is_awaiting())
        self.assertEqual(1000, charge.cc_received_total)
        self.assertEqual(1, charge.confirmations)
        self.assertTrue(charge.paid_at)

    def test_unpaid_to_fully_confirmed(self):
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         status='awaiting',
                                         pay_status='unpaid')
        height = 1
        current_height = 2
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(900, height - 1), Credit.confirmed(99, height), Credit.confirmed(1, height)], current_height, db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_confirmed())
        self.assertTrue(charge.is_completed())
        self.assertEqual(1000, charge.cc_received_total)
        self.assertEqual(2, charge.confirmations)
        self.assertTrue(charge.paid_at)

    # awaiting: underpaid

    def test_underpaid_to_expired(self):
        minutes_15 = 15*60*1000
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=900,
                                         status='awaiting',
                                         pay_status='underpaid',
                                         timeout_ms=minutes_15,
                                         created_at=utc_ago(minutes=18))
        uc = StubRefreshChargeUC(charge.uid, [Credit.unconfirmed(900)], db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_underpaid())
        self.assertTrue(charge.is_expired())

    def test_underpaid_to_less_underpaid(self):
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=900,
                                         status='awaiting',
                                         pay_status='underpaid')
        uc = StubRefreshChargeUC(charge.uid, [Credit.unconfirmed(900), Credit.unconfirmed(99)], db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_underpaid())
        self.assertTrue(charge.is_awaiting())
        self.assertEqual(999, charge.cc_received_total)

    def test_underpaid_to_paid(self):
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=900,
                                         status='awaiting',
                                         pay_status='underpaid')
        uc = StubRefreshChargeUC(charge.uid, [Credit.unconfirmed(900), Credit.unconfirmed(99), Credit.unconfirmed(2)], db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_paid())
        self.assertTrue(charge.is_awaiting())
        self.assertEqual(1001, charge.cc_received_total)

    def test_underpaid_to_confirmed(self):
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=900,
                                         status='awaiting',
                                         pay_status='underpaid')
        current_height = 1
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(900, 1), Credit.confirmed(101, 1)], current_height, db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_confirmed())
        self.assertTrue(charge.is_awaiting())
        self.assertEqual(1001, charge.cc_received_total)
        self.assertEqual(1, charge.confirmations)
        self.assertEqual(1, charge.confirmations)

    def test_underpaid_to_completed(self):
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=900,
                                         status='awaiting',
                                         pay_status='underpaid')
        current_height = 2
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(900, 1), Credit.confirmed(101, 1)], current_height, db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_confirmed())
        self.assertTrue(charge.is_completed())
        self.assertEqual(1001, charge.cc_received_total)
        self.assertEqual(2, charge.confirmations)

    # awaiting: paid

    def test_paid_to_expired(self):
        minutes_60 = 60*60*1000
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=1000,
                                         status='awaiting',
                                         pay_status='paid',
                                         timeout_to_complete_ms=minutes_60,
                                         created_at=utc_ago(minutes=61))
        uc = StubRefreshChargeUC(charge.uid, [Credit.unconfirmed(1000)], db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_paid())
        self.assertTrue(charge.is_expired())

    def test_paid_to_paid_overpayment(self):
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=1000,
                                         status='awaiting',
                                         pay_status='paid')
        uc = StubRefreshChargeUC(charge.uid, [Credit.unconfirmed(1000), Credit.unconfirmed(1)], db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_paid())
        self.assertTrue(charge.is_awaiting())
        self.assertEqual(1001, charge.cc_received_total)
        self.assertTrue(charge.is_overpaid())

    def test_paid_to_confirmed(self):
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=1000,
                                         status='awaiting',
                                         pay_status='paid')
        current_height = 1
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(1000, 1)], current_height, db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_confirmed())
        self.assertTrue(charge.is_awaiting())
        self.assertEqual(1000, charge.cc_received_total)
        self.assertEqual(1, charge.confirmations)

    def test_paid_to_completed(self):
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=1000,
                                         status='awaiting',
                                         pay_status='paid')
        current_height = 2
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(1000, 1)], current_height, db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_confirmed())
        self.assertTrue(charge.is_completed())
        self.assertEqual(1000, charge.cc_received_total)
        self.assertEqual(2, charge.confirmations)

    # awaiting: confirmed

    def test_confirmed_to_expired(self):
        minutes_60 = 60*60*1000
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=1000,
                                         status='awaiting',
                                         pay_status='confirmed',
                                         timeout_to_complete_ms=minutes_60,
                                         created_at=utc_ago(minutes=61))
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(1000, 1)], db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_confirmed())
        self.assertTrue(charge.is_expired())

    def test_confirmed_to_confirmed_overpayment(self):
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=1000,
                                         status='awaiting',
                                         pay_status='confirmed')
        current_height = 1
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(1000, 1), Credit.confirmed(1, 1)], current_height, db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_confirmed())
        self.assertTrue(charge.is_awaiting())
        self.assertEqual(1001, charge.cc_received_total)
        self.assertEqual(1, charge.confirmations)

    def test_confirmed_to_completed(self):
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=1000,
                                         status='awaiting',
                                         pay_status='confirmed')
        current_height = 2
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(1000, 1)], current_height, db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_confirmed())
        self.assertTrue(charge.is_completed())
        self.assertEqual(1000, charge.cc_received_total)
        self.assertEqual(2, charge.confirmations)

    # completed

    def test_completed_does_not_expire(self):
        minutes_60 = 60*60*1000
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=1000,
                                         status='completed',
                                         pay_status='confirmed',
                                         timeout_to_complete_ms=minutes_60,
                                         created_at=utc_ago(minutes=61))
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(1000, 1)], db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_confirmed())
        self.assertTrue(charge.is_completed())
        self.assertEqual(1000, charge.cc_received_total)

    def test_completed_to_completed_unpaid(self):
        # This means merchant got cheated because CypherpunkPay's assumptions about when it is safe to complete
        # were overly optimistic. Either the chain was rolled back or 0-confs were accepted that later disappeared
        # from explorers' mempools.
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=1000,
                                         status='completed',
                                         pay_status='confirmed')
        uc = StubRefreshChargeUC(charge.uid, [], db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_unpaid())
        self.assertTrue(charge.is_completed())
        self.assertEqual(0, charge.cc_received_total)

    def test_completed_to_completed_underpaid(self):
        # This means merchant got cheated because CypherpunkPay's assumptions about when it is safe to complete
        # were overly optimistic. Either the chain was rolled back or 0-confs were accepted that later disappeared
        # from explorers' mempools.
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=1000,
                                         status='completed',
                                         pay_status='confirmed')
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(900, 1)], db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_underpaid())
        self.assertTrue(charge.is_completed())
        self.assertEqual(900, charge.cc_received_total)

    def test_completed_to_completed_overpaid(self):
        # This means user accidentally sent money again to the charge that was already completed.
        # We still want to recognize such accidental overpayments so we continue to track completed charges.
        # This will help with refunds.
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         cc_received_total=1000,
                                         status='completed',
                                         pay_status='confirmed')
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(1000, 1), Credit.confirmed(1, 1)], db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_confirmed())
        self.assertTrue(charge.is_completed())
        self.assertEqual(1001, charge.cc_received_total)

    # expired

    def test_expired_does_not_complete(self):
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         status='expired',
                                         pay_status='unpaid')
        height = 1
        current_height = 2
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(1000, height)], current_height, db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_confirmed())
        self.assertTrue(charge.is_expired())
        self.assertEqual(1000, charge.cc_received_total)
        self.assertEqual(2, charge.confirmations)

    def test_expired_unpaid_to_expired_confirmed(self):
        # This means user accidently sent money to charge that expired.
        # We still want to recognize such transactions so we continue to track expired charges.
        # This is to facilitate refunds.
        charge = ExampleCharge.db_create(self.db,
                                         total=1000,
                                         status='expired',
                                         pay_status='unpaid')
        height = 1
        current_height = 1
        uc = StubRefreshChargeUC(charge.uid, [Credit.confirmed(1000, height)], current_height, db=self.db)
        uc.exec()
        self.db.reload(charge)
        self.assertTrue(charge.is_confirmed())
        self.assertTrue(charge.is_expired())
        self.assertEqual(1000, charge.cc_received_total)
        self.assertEqual(1, charge.confirmations)

    # Lightning

    def test_lightning_unpaid_to_completed(self):
        charge = Charge(total=self.ONE_SATOSHI, currency='btc', time_to_pay_ms=15*60*1000, time_to_complete_ms=60*60*1000)
        charge.cc_total = charge.total
        charge.activated_at = utc_now()
        charge.status = 'awaiting'
        charge.cc_lightning_payment_request = self.EXAMPLE_PAYMENT_REQUEST_TESTNET
        self.db.insert(charge)

        uc = StubLnRefreshChargeUC(charge.uid, [Credit.confirmed(Decimal('0.00000001'), 1000)], db=self.db)
        uc.exec()
        self.db.reload(charge)

        assert charge.is_confirmed()
        assert charge.is_completed()
        assert charge.cc_received_total == Decimal('0.00000001')
        assert charge.paid_at is not None
        assert charge.completed_at is not None

    # Mock checking fetch_credits_from_lightning_node will NOT be called
    class MockLnRefreshChargeUC(RefreshChargeUC):
        def __init__(self, charge_uid: str, db=None):
            self._blockchain_height = 2**31  # just big
            super().__init__(charge_uid, current_height=self._blockchain_height, db=db, http_client=DummyHttpClient(), config=ExampleConfig())

        def fetch_credits_from_lightning_node(self, charge):
            raise Exception('This method should not be called -> test case failed')

    def test_lightning_expired_wont_refresh(self):
        charge = Charge(total=self.ONE_SATOSHI, currency='btc', time_to_pay_ms=1, time_to_complete_ms=60*60*1000)
        charge.cc_total = charge.total
        charge.activated_at = utc_now()
        charge.status = 'expired'
        charge.pay_status = 'unpaid'
        charge.cc_lightning_payment_request = self.EXAMPLE_PAYMENT_REQUEST_TESTNET
        self.db.insert(charge)

        uc = self.MockLnRefreshChargeUC(charge.uid, db=self.db)
        uc.exec()  # should not call LND (checked by the mock)

    def test_lightning_completed_wont_refresh(self):
        charge = Charge(total=self.ONE_SATOSHI, currency='btc', time_to_pay_ms=1, time_to_complete_ms=60*60*1000)
        charge.cc_total = charge.total
        charge.cc_received_total = charge.cc_total
        charge.activated_at = utc_now()
        charge.paid_at = utc_now()
        charge.pay_status = 'paid'
        charge.status = 'completed'
        charge.cc_lightning_payment_request = self.EXAMPLE_PAYMENT_REQUEST_TESTNET
        self.db.insert(charge)

        uc = self.MockLnRefreshChargeUC(charge.uid, db=self.db)
        uc.exec()  # should not call LND (checked by the mock)
