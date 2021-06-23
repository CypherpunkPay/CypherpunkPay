from apscheduler.job import Job

from cypherpunkpay.common import *
from cypherpunkpay.jobs.job_scheduler import JobScheduler
from cypherpunkpay.models.job_report import JobReport
from cypherpunkpay.usecases import UseCase


class ReportJobsUC(UseCase):

    _jobs: List[Job] = None

    def __init__(self, scheduler: JobScheduler):
        self._jobs = scheduler.get_all_jobs()

    def exec(self) -> JobReport:
        report = JobReport()
        report.total = len(self._jobs)
        report.jobs_by_next_run = sorted(self._jobs, key=lambda job: job.next_run_time)
        #report.jobs_by_type = {}
        return report
