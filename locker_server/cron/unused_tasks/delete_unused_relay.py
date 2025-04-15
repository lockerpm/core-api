import time
import schedule

from django.db import close_old_connections

from locker_server.containers.containers import cron_task_service, relay_subdomain_service
from locker_server.cron.task import Task
from locker_server.shared.utils.app import now


class DeleteUnusedRelay(Task):
    def __init__(self):
        super(DeleteUnusedRelay, self).__init__()
        self.job_id = 'delete_unused_relay'

    def register_job(self):
        pass

    def log_job_execution(self, run_time: float, exception: str = None, tb: str = None):
        pass

    def real_run(self, *args):
        # Close old connections
        close_old_connections()
        current_time = now()
        latest_used_time_pivot = current_time - 90 * 86400
        # Delete unused relay subdomains
        relay_subdomain_service.delete_unused_subdomain_relay_addresses(latest_used_time_pivot=latest_used_time_pivot)

    def scheduling(self):
        schedule.every().day.at("20:00").do(self.run)
        while True:
            schedule.run_pending()
            time.sleep(1)
