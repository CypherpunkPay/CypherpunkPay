import logging as log


class Job(object):
    """ Simple labda jobs wrapper to log exceptions """

    def __init__(self, job, job_id):
        self.job = job
        self.job_id = job_id

    def __call__(self, *args, **kwargs):
        try:
            self.job()
        except BaseException as e:
            log.exception(f'Job "{self.job_id}" raised exception')
