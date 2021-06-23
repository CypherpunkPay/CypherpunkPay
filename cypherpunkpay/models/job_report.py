from apscheduler.job import Job

from cypherpunkpay.common import *


class JobReport(object):

    #jobs_by_type: Dict[str, Job] = {}
    jobs_by_next_run: List[Job] = []      # Only the first occurence
    total: int = 0

    def jobs_scheduled_until(self, dt: datetime.datetime):
        counter = 0
        for job in self.jobs_by_next_run:
            runtimes = job._get_run_times(dt)
            counter += len(runtimes)
        return counter
