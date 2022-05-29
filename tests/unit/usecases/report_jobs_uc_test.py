from apscheduler.triggers.interval import IntervalTrigger

from cypherpunkpay.globals import *
from cypherpunkpay.jobs.job_scheduler import JobScheduler
from cypherpunkpay.usecases.report_jobs_uc import ReportJobsUC

from tests.unit.db_test_case import CypherpunkpayDBTestCase


class ReportJobsUCTest(CypherpunkpayDBTestCase):

    def setup_method(self):
        self.job_scheduler = JobScheduler()

    def teardown_method(self):
        self.job_scheduler.shutdown()

    def test_exec(self):
        def no_op(): pass

        self.job_scheduler.add_job(no_op, id='refresh_job_rwer334', trigger=IntervalTrigger(minutes=2))
        self.job_scheduler.add_job(no_op, id='refresh_job_3423ref', trigger=IntervalTrigger(seconds=2))
        self.job_scheduler.add_job(no_op, id='refresh_job_gj3u4t9', trigger=IntervalTrigger(minutes=30))

        jobs = self.job_scheduler.get_all_jobs()

        report = ReportJobsUC(self.job_scheduler).exec()

        # total
        self.assertEqual(3, report.total)

        # jobs_by_next_run
        self.assertEqual('refresh_job_3423ref', report.jobs_by_next_run[0].id)
        self.assertEqual('refresh_job_rwer334', report.jobs_by_next_run[1].id)
        self.assertEqual('refresh_job_gj3u4t9', report.jobs_by_next_run[2].id)

        # jobs_scheduled_until
        count = report.jobs_scheduled_until(utc_from_now(seconds=11))
        self.assertEqual(5, count)
