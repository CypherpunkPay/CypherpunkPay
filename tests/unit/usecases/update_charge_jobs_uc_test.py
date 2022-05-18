from apscheduler.job import Job
from apscheduler.triggers.interval import IntervalTrigger

from cypherpunkpay.globals import *
from cypherpunkpay.jobs.job_scheduler import JobScheduler
from cypherpunkpay.usecases.update_charge_jobs_uc import UpdateChargeJobsUC
from cypherpunkpay.models.charge import ExampleCharge
from tests.unit.db_test_case import CypherpunkpayDBTestCase


class UpdateChargeJobsUCTest(CypherpunkpayDBTestCase):

    TRIGGER_1s = IntervalTrigger(seconds=1)
    EXPECTED_INTERVAL_FOR_AWAITING_PAYMENT = 2  # 2 seconds
    EXPECTED_INTERVAL_FOR_AWAITING_CONFIRMATION = 15  # 15 seconds
    EXPECTED_INTERVAL_FOR_FINAL = 30 * 60  # 30 minutes

    def setUp(self):
        super().setUp()
        self.job_scheduler = JobScheduler()
        self.job_scheduler.pause()  # we don't want any jobs to actually run during the tests

    def tearDown(self):
        self.job_scheduler.shutdown()
        super().tearDown()

    def test_blank_slate(self):
        UpdateChargeJobsUC(self.job_scheduler, self.db).exec()
        self.assertEmpty(self.job_scheduler.get_all_jobs())

    def test_removes_jobs_for_old_charges(self):
        before_threshold_date = utc_ago(days=8)
        within_threshold_date = utc_ago(days=6)

        ExampleCharge.db_create(self.db, uid='1', created_at=before_threshold_date),
        ExampleCharge.db_create(self.db, uid='2', created_at=within_threshold_date),
        ExampleCharge.db_create(self.db, uid='3'),
        ExampleCharge.db_create(self.db, uid='4')

        self.job_scheduler.add_job(None, id="refresh_charge_1", trigger=self.TRIGGER_1s)
        self.job_scheduler.add_job(None, id="refresh_charge_2", trigger=self.TRIGGER_1s)
        self.job_scheduler.add_job(None, id="refresh_charge_3", trigger=self.TRIGGER_1s)
        self.job_scheduler.add_job(None, id="refresh_charge_4", trigger=self.TRIGGER_1s)
        self.job_scheduler.add_job(None, id="refresh_charge_5", trigger=self.TRIGGER_1s)
        self.job_scheduler.add_job(None, id="unrelated_job_1", trigger=self.TRIGGER_1s)

        UpdateChargeJobsUC(self.job_scheduler, self.db).exec()

        updated_jobs = [job.id for job in self.job_scheduler.get_all_jobs()]
        self.assertTrue('refresh_charge_1' not in updated_jobs)
        self.assertTrue('refresh_charge_2' in updated_jobs)
        self.assertTrue('refresh_charge_3' in updated_jobs)
        self.assertTrue('refresh_charge_4' in updated_jobs)
        self.assertTrue('refresh_charge_5' not in updated_jobs)
        self.assertTrue('unrelated_job_1' in updated_jobs)

    def test_adds_jobs_for_new_charges(self):
        ExampleCharge.db_create(self.db, uid='1'),
        ExampleCharge.db_create(self.db, uid='2', pay_status='unpaid', status='awaiting'),
        ExampleCharge.db_create(self.db, uid='3', pay_status='confirmed', status='completed', paid_at=utc_now()),
        ExampleCharge.db_create(self.db, uid='4')

        self.job_scheduler.add_job(None, id="refresh_charge_1", trigger=self.TRIGGER_1s)
        self.job_scheduler.add_job(None, id="refresh_charge_4", trigger=self.TRIGGER_1s)

        UpdateChargeJobsUC(self.job_scheduler, self.db).exec()

        updated_jobs = [job.id for job in self.job_scheduler.get_all_jobs()]
        self.assertEqual(4, len(updated_jobs))
        self.assertTrue('refresh_charge_1' in updated_jobs)
        self.assertTrue('refresh_charge_2' in updated_jobs)
        self.assertTrue('refresh_charge_3' in updated_jobs)
        self.assertTrue('refresh_charge_4' in updated_jobs)

        job_2: Job = first(lambda job: job.id == 'refresh_charge_2', self.job_scheduler.get_all_jobs())
        self.assertEqual(self.EXPECTED_INTERVAL_FOR_AWAITING_PAYMENT, round(job_2.trigger.interval_length))

        job_3: Job = first(lambda job: job.id == 'refresh_charge_3', self.job_scheduler.get_all_jobs())
        self.assertEqual(self.EXPECTED_INTERVAL_FOR_FINAL, round(job_3.trigger.interval_length))

    def test_reschedules_jobs_according_to_charge_state(self):
        ExampleCharge.db_create(self.db, uid='1', pay_status='unpaid', status='draft'),
        ExampleCharge.db_create(self.db, uid='2', pay_status='unpaid', status='awaiting'),
        ExampleCharge.db_create(self.db, uid='3', pay_status='underpaid', status='awaiting'),
        ExampleCharge.db_create(self.db, uid='4', pay_status='paid', status='awaiting', paid_at=utc_ago(minutes=3)),
        ExampleCharge.db_create(self.db, uid='5', pay_status='confirmed', status='awaiting', paid_at=utc_ago(minutes=20)),
        ExampleCharge.db_create(self.db, uid='6', pay_status='confirmed', status='completed', paid_at=utc_ago(minutes=120))
        ExampleCharge.db_create(self.db, uid='7', pay_status='unpaid', status='expired')
        ExampleCharge.db_create(self.db, uid='8', pay_status='paid', status='expired', paid_at=utc_ago(days=3))
        ExampleCharge.db_create(self.db, uid='9', pay_status='unpaid', status='cancelled')

        self.job_scheduler.add_job(None, id="refresh_charge_1", trigger=self.TRIGGER_1s)  # should be removed because it is draft charge
        self.job_scheduler.add_job(None, id="refresh_charge_2", trigger=self.TRIGGER_1s)
        self.job_scheduler.add_job(None, id="refresh_charge_3", trigger=self.TRIGGER_1s)
        self.job_scheduler.add_job(None, id="refresh_charge_4", trigger=self.TRIGGER_1s)
        self.job_scheduler.add_job(None, id="refresh_charge_5", trigger=self.TRIGGER_1s)
        self.job_scheduler.add_job(None, id="refresh_charge_6", trigger=self.TRIGGER_1s)
        self.job_scheduler.add_job(None, id="refresh_charge_7", trigger=self.TRIGGER_1s)
        self.job_scheduler.add_job(None, id="refresh_charge_8", trigger=self.TRIGGER_1s)
        self.job_scheduler.add_job(None, id="refresh_charge_9", trigger=self.TRIGGER_1s)

        UpdateChargeJobsUC(self.job_scheduler, self.db).exec()

        updated_jobs = self.job_scheduler.get_all_jobs()
        self.assertEqual(8, len(updated_jobs))

        self.assertFalse(first(lambda job: job.id == 'refresh_charge_1'), updated_jobs)

        job_2: Job = first(lambda job: job.id == 'refresh_charge_2', updated_jobs)
        self.assertEqual(self.EXPECTED_INTERVAL_FOR_AWAITING_PAYMENT, round(job_2.trigger.interval_length))

        job_3: Job = first(lambda job: job.id == 'refresh_charge_3', updated_jobs)
        self.assertEqual(self.EXPECTED_INTERVAL_FOR_AWAITING_PAYMENT, round(job_3.trigger.interval_length))

        job_4: Job = first(lambda job: job.id == 'refresh_charge_4', updated_jobs)
        self.assertEqual(self.EXPECTED_INTERVAL_FOR_AWAITING_CONFIRMATION, round(job_4.trigger.interval_length))

        job_5: Job = first(lambda job: job.id == 'refresh_charge_5', updated_jobs)
        self.assertEqual(self.EXPECTED_INTERVAL_FOR_AWAITING_CONFIRMATION, round(job_5.trigger.interval_length))

        job_6: Job = first(lambda job: job.id == 'refresh_charge_6', updated_jobs)
        self.assertEqual(self.EXPECTED_INTERVAL_FOR_FINAL, round(job_6.trigger.interval_length))

        job_7: Job = first(lambda job: job.id == 'refresh_charge_7', updated_jobs)
        self.assertEqual(self.EXPECTED_INTERVAL_FOR_FINAL, round(job_7.trigger.interval_length))

        job_8: Job = first(lambda job: job.id == 'refresh_charge_8', updated_jobs)
        self.assertEqual(self.EXPECTED_INTERVAL_FOR_FINAL, round(job_8.trigger.interval_length))

        job_9: Job = first(lambda job: job.id == 'refresh_charge_9', updated_jobs)
        self.assertEqual(self.EXPECTED_INTERVAL_FOR_FINAL, round(job_9.trigger.interval_length))
