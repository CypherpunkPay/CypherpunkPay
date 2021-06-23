from apscheduler.triggers import interval

from cypherpunkpay.common import *


class JobAdder(object):

    def __init__(self, app):
        self._app = app

    def add_full_time_jobs(self):
        scheduler = self._app.job_scheduler()

        trigger = interval.IntervalTrigger(seconds=60)
        scheduler.add_job(
            lambda: self._app.price_tickers().update(),
            id='update_price_tickers',
            name='update_price_tickers',
            trigger=trigger,
            next_run_time=utc_now()
        )

        from cypherpunkpay.usecases.update_all_blockchains_height_uc import UpdateAllBlockchainsHeightUC
        trigger = interval.IntervalTrigger(seconds=10)
        scheduler.add_job(
            lambda: UpdateAllBlockchainsHeightUC().exec(),
            id='update_blockchain_height',
            name="update_blockchain_height",
            trigger=trigger,
            next_run_time=utc_now()
        )

        from cypherpunkpay.usecases.update_charge_jobs_uc import UpdateChargeJobsUC
        trigger = interval.IntervalTrigger(seconds=2)
        scheduler.add_job(
            lambda: UpdateChargeJobsUC(scheduler, self._app.db()).exec(),
            id='update_charge_jobs',
            name="update_charge_jobs",
            trigger=trigger
        )

        if self._app.config().merchant_enabled():
            from cypherpunkpay.usecases.notify_merchant_of_all_completions_uc import NotifyMerchantOfAllCompletionsUC
            trigger = interval.IntervalTrigger(seconds=4)
            scheduler.add_job(
                lambda: NotifyMerchantOfAllCompletionsUC(self._app.db()).exec(),
                id='notify_merchant_of_all_completions',
                name="notify_merchant_of_all_completions",
                trigger=trigger
            )

        from cypherpunkpay.usecases.log_stats_uc import LogStatsUC
        trigger = interval.IntervalTrigger(seconds=10)
        scheduler.add_job(
            lambda: LogStatsUC(self._app).exec(),
            id='log_stats',
            name="log_stats",
            trigger=trigger
        )

        if self._app.config().dev_env():
            from cypherpunkpay.db.dev_examples import DevExamples
            # This is attempted in perpetuity because we wait for App to be fully initialized (prices etc)
            trigger = interval.IntervalTrigger(seconds=2)
            scheduler.add_job(
                lambda: (DevExamples().create_all_if_missing() if self._app.is_fully_initialized() else None),
                id='create_dev_examples',
                name="create_dev_examples",
                trigger=trigger
            )
