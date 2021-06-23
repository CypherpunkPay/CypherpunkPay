import atexit

from apscheduler.job import Job
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler

from cypherpunkpay.common import *


class JobScheduler(object):
    """ Convenience wrapper around AppScheduler """

    _scheduler: BackgroundScheduler = None

    def __init__(self):
        self._scheduler = BackgroundScheduler(
            job_defaults={
                'misfire_grace_time': 60,  # the call can only be delayed this number of seconds; otherwise it is cancelled
                'coalesce': True,          # run only once even if multiple calls got queued due to some delays
                'max_instances': 1         # maximum number of concurrently running instances allowed for this job
            }
        )
        self._scheduler.start()
        atexit.register(lambda: self.shutdown())

    def get_all_jobs(self) -> List[Job]:
        return self._scheduler.get_jobs()

    def remove_job(self, job_id) -> None:
        try:
            log.debug(f'Removing job "{job_id}"')
            self._scheduler.remove_job(job_id)
        except JobLookupError:
            pass  # it is fine to remove job multiple times

    def add_job(self, func, **kwargs) -> Job:
        job_id = kwargs.get("id")
        job_trigger = kwargs.get("trigger")
        log.debug(f'Adding job "{job_id}" w/ trigger {job_trigger}')
        from cypherpunkpay.jobs.job import Job
        wrapped_func = Job(func, job_id)
        return self._scheduler.add_job(wrapped_func, **kwargs)

    def pause(self):
        self._scheduler.pause()

    def shutdown(self):
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)


class DummyJobScheduler(object):
    def get_all_jobs(self) -> List[Job]: return []
    def remove_job(self, job_id) -> None: pass
    def add_job(self, func, **kwargs) -> Job: pass
    def shutdown(self): pass
