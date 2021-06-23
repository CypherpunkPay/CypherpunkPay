from cypherpunkpay.common import *
from cypherpunkpay.db.db import DB
from cypherpunkpay.db.sqlite_db import db_int8_to_decimal     # this should be in DB; layers violation
from cypherpunkpay.models.charge_report import ChargeReport
from cypherpunkpay.usecases import UseCase


class ReportChargesUC(UseCase):

    _db: DB = None

    def __init__(self, db: DB):
        self._db = db

    def exec(self) -> (ChargeReport, ChargeReport):
        by_status = self._db.count_and_sum_charges_grouped_by_status(activated_after=utc_ago(days=7))
        report_7d = self.row_to_report(by_status)

        by_status = self._db.count_and_sum_charges_grouped_by_status(activated_after=utc_ago(weeks=54 * 32))
        report_all_time = self.row_to_report(by_status)

        return report_7d, report_all_time

    def row_to_report(self, by_status) -> ChargeReport:
        report = ChargeReport()
        for row in by_status:
            status = row[0]
            count = int(row[1])
            total = db_int8_to_decimal(row[2])
            if status == 'awaiting':
                report.awaiting = count
            if status == 'completed':
                report.completed = count
                report.completed_usd = total
            if status == 'expired':
                report.expired = count
            if status == 'cancelled':
                report.cancelled = count
        return report
