import time
import schedule

from django.db import close_old_connections

from locker_server.containers.containers import attachment_service
from locker_server.cron.task import Task
from locker_server.shared.constants.attachments import OVERSIZE_ATTACHMENT_CHECK_WINDOW
from locker_server.shared.utils.app import now


class DeleteOversizeAttachments(Task):
    def __init__(self):
        super(DeleteOversizeAttachments, self).__init__()
        self.job_id = 'delete_oversize_attachments'

    def register_job(self):
        pass

    def log_job_execution(self, run_time: float, exception: str = None, tb: str = None):
        pass

    def real_run(self, *args):
        # Close old connections
        close_old_connections()
        # The presigned PUT urls do not limit the file size => Delete the recent uploaded files which are too large
        attachment_service.delete_oversize_attachments(modified_after=now() - OVERSIZE_ATTACHMENT_CHECK_WINDOW)

    def scheduling(self):
        schedule.every().hour.do(self.run)
        while True:
            schedule.run_pending()
            time.sleep(1)
