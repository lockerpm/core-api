import os
import time
import schedule
import requests
from datetime import datetime

from django.db import close_old_connections
from django.db.models import OuterRef, Subquery, CharField

from cron.task import Task
from cystack_models.models.users.users import User
from cystack_models.models.users.devices import Device
from shared.log.cylog import CyLog
from shared.services.spreadsheet.spreadsheet import LockerSpreadSheet, HEADERS, API_USERS
from shared.utils.app import now


class Feedback(Task):
    def __init__(self):
        super(Feedback, self).__init__()
        self.job_id = 'feedback'

    def register_job(self):
        pass

    def log_job_execution(self, run_time: float, exception: str = None, tb: str = None):
        pass

    def real_run(self, *args):
        # Close old connections
        close_old_connections()
        try:
            self.log_new_users()
        except Exception as e:
            self.logger.error()
        # self.upgrade_survey_emails()

    def upgrade_survey_emails(self):
        spread_sheet = LockerSpreadSheet()
        spread_sheet.upgrade_survey_email()

    def log_new_users(self):
        current_time = now()
        current_time_str = datetime.fromtimestamp(now()).strftime("%d-%b-%Y")

        devices = Device.objects.filter(user_id=OuterRef("user_id")).order_by('last_login')
        users = User.objects.filter(activated=True)
        new_users = users.filter(
            activated=True,
            activated_date__lte=current_time, activated_date__gt=current_time - 86400
        ).annotate(
            first_device_client_id=Subquery(devices.values('client_id')[:1], output_field=CharField()),
            first_device_name=Subquery(devices.values('device_name')[:1], output_field=CharField()),
        ).order_by('activated_date').values('user_id', 'first_device_client_id', 'first_device_name')

        user_ids = [new_user.get("user_id") for new_user in new_users]
        users_res = requests.post(url=API_USERS, headers=HEADERS, json={"ids": user_ids, "emails": []})
        if users_res.status_code != 200:
            CyLog.error(**{"message": "[log_new_users] Get users from Gateway error: {} {}".format(
                users_res.status_code, users_res.text
            )})
            users_data = []
        else:
            users_data = users_res.json()

        notification = ""
        for new_user in new_users:
            user_data = next(
                (item for item in users_data if item["id"] == new_user.get("user_id")), {}
            )
            notification += "{} - {} - {}\n".format(
                user_data.get("email") or new_user.get("user_id"),
                new_user.get("first_device_client_id"),
                new_user.get("first_device_name"),
            )

        CyLog.info(**{
            "message": "Date: {}\nTotal: {}\nNew users: {}\n{}".format(
                current_time_str, users.count(), len(new_users), notification
            ),
            "output": ["slack_new_users"]
        })

    def scheduling(self):
        if os.getenv("PROD_ENV") != "staging":
            schedule.every().day.at("10:00").do(self.run)
            while True:
                schedule.run_pending()
                time.sleep(1)
