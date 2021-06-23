from threading import RLock
import random

from apscheduler.job import Job
from apscheduler.triggers.interval import IntervalTrigger

from cypherpunkpay.common import *
from cypherpunkpay.db.db import DB
from cypherpunkpay.models.charge import Charge
from cypherpunkpay.jobs.job_scheduler import JobScheduler
from cypherpunkpay.usecases import UseCase


class UpdateChargeJobsUC(UseCase):

    _lock = RLock()  # could be per job_scheduler instead of global but nvm that

    _job_scheduler: JobScheduler
    _db: DB
    _recent_charges: List[Charge]
    _jobs: List[Job]

    def __init__(self, job_scheduler, db):
        self._job_scheduler = job_scheduler
        self._db = db

    def exec(self):
        with self._lock:
            self._recent_charges = self._db_get_recently_activated_charges()
            self._jobs = self._get_refresh_jobs()
            self._remove_jobs_for_old_charges()
            self._ensure_jobs_for_recent_charges()

    # MOCKME
    def _db_get_recently_activated_charges(self) -> List[Charge]:
        return self._db.get_recently_activated_charges(datetime.timedelta(days=7))

    def _get_refresh_jobs(self):
        return list(filter(lambda job: job.id.startswith('refresh_charge_'), self._job_scheduler.get_all_jobs()))

    def _remove_jobs_for_old_charges(self):
        for job in self._jobs:
            if self._no_recent_charge_for(job):
                self._job_scheduler.remove_job(job.id)

    def _no_recent_charge_for(self, refresh_job: Job):
        return not any(refresh_job.id == charge.refresh_job_id() for charge in self._recent_charges)

    def _ensure_jobs_for_recent_charges(self):
        from cypherpunkpay.usecases.refresh_charge_uc import RefreshChargeUC
        for charge in self._recent_charges:
            job = self._job_for_charge(charge)
            if job:
                # Reschedule if necessary
                trigger = self._trigger_for_charge(charge)
                if job.trigger.interval_length != trigger.interval_length:
                    job.reschedule(trigger)
            else:
                # Add the job
                trigger = self._trigger_for_charge(charge)
                self._job_scheduler.add_job(
                    lambda c=charge: RefreshChargeUC(c.uid).exec(),
                    id=charge.refresh_job_id(),
                    name=charge.refresh_job_id(),
                    trigger=trigger,
                    next_run_time=utc_from_now(seconds=random.randint(1, 6))  # the *first* run should be pretty immediate; this is for long-period jobs to make them run *soon* after CypherpunkPay restart
                )

    # Depending on charge status, we want it to be refreshed often or rarely
    def _trigger_for_charge(self, charge: Charge) -> IntervalTrigger:
        # Final charges are unlikely to change but technically they can still receive payments (maybe due to late network confirmation or user error)
        if charge.has_final_status():
            return IntervalTrigger(minutes=30)

        # Paid but awaiting (more) confirmations
        if charge.is_paid() or charge.is_confirmed():
            if charge.paid_at > utc_ago(hours=1):
                return IntervalTrigger(seconds=15)
            elif charge.paid_at > utc_ago(hours=12):
                return IntervalTrigger(minutes=3)
            else:
                return IntervalTrigger(minutes=15)

        # Draft, unpaid or underpaid
        return IntervalTrigger(seconds=2)

    def _job_for_charge(self, charge: Charge) -> Job:
        return first_true(self._jobs, pred=lambda job: job.id == charge.refresh_job_id(), default=None)

    def _no_job_for(self, charge: Charge):
        return not any(refresh_job.id == charge.refresh_job_id() for refresh_job in self._jobs)
