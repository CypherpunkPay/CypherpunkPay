from cypherpunkpay.common import *
from cypherpunkpay.models.charge import ExampleCharge
from cypherpunkpay.usecases.report_charges_uc import ReportChargesUC

from tests.unit.db_test_case import CypherpunkpayDBTestCase


class ReportChargesUCTest(CypherpunkpayDBTestCase):

    def test_exec(self):
        # within 7 days
        ExampleCharge.db_create(self.db, status='awaiting', activated_at=utc_ago(days=6, hours=23, minutes=59))
        ExampleCharge.db_create(self.db, status='completed')
        ExampleCharge.db_create(self.db, status='expired')
        ExampleCharge.db_create(self.db, status='expired')
        ExampleCharge.db_create(self.db, status='cancelled')
        ExampleCharge.db_create(self.db, status='completed')
        ExampleCharge.db_create(self.db, status='expired')
        # older than 7 days
        ExampleCharge.db_create(self.db, status='expired', activated_at=utc_ago(days=7, seconds=1))
        ExampleCharge.db_create(self.db, status='completed', activated_at=utc_ago(days=10_000))

        report_7d, report_all_time = ReportChargesUC(self.db).exec()

        # Report 7 days
        self.assertEqual(1, report_7d.awaiting)
        self.assertEqual(2, report_7d.completed)
        self.assertEqual(3, report_7d.expired)
        self.assertEqual(1, report_7d.cancelled)

        # Report all time
        self.assertEqual(1, report_all_time.awaiting)
        self.assertEqual(3, report_all_time.completed)
        self.assertEqual(4, report_all_time.expired)
        self.assertEqual(1, report_all_time.cancelled)
