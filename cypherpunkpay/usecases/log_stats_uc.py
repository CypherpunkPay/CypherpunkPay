from cypherpunkpay import Config, App
from cypherpunkpay.common import *
from cypherpunkpay.usecases import UseCase
from cypherpunkpay.usecases.report_charges_uc import ReportChargesUC
from cypherpunkpay.usecases.report_jobs_uc import ReportJobsUC


class LogStatsUC(UseCase):

    def __init__(self, app: App):
        self._app = app

    def exec(self):
        cr_7d, cr_all_time = ReportChargesUC(self._app.db()).exec()
        msg = f'Charge stats: \
                  in_progress={cr_all_time.awaiting} \
                  7d_completed={cr_7d.completed} ({cr_7d.completed_percent}%) \
                  all_time_completed={cr_all_time.completed} ({cr_all_time.completed_percent}%)'
        msg = re.sub(r'\s{1,}', ' ', msg)
        self._log_charge_stats(msg)

        job_report = ReportJobsUC(self._app.job_scheduler()).exec()
        msg = f'Job stats: \
                  total={job_report.total} \
                  run_next_1m={job_report.jobs_scheduled_until(utc_from_now(minutes=1))}'
        msg = re.sub(r'\s{1,}', ' ', msg)
        self._log_job_stats('   ' + msg)

        msg = 'Chain stats: '
        for coin in self._app.config().configured_coins():
            msg += f"{coin}_height={self._app.current_blockchain_height(coin)} ({self._app.config().cc_network(coin)})  "
        log.info(' ' + msg.strip())

    # MOCK ME
    def _log_job_stats(self, msg):
        log.info(msg)

    # MOCK ME
    def _log_charge_stats(self, msg):
        log.info(msg)
