import io
from typing import Tuple, Dict, List, Optional, NoReturn

import django_rq
import xlsxwriter

from locker_server.core.entities.enterprise.member.enterprise_member import EnterpriseMember
from locker_server.core.entities.event.event import Event
from locker_server.core.repositories.event_repository import EventRepository
from locker_server.core.repositories.user_repository import UserRepository
from locker_server.shared.external_services.locker_background.impl import NotifyBackground
from locker_server.shared.log.cylog import CyLog
from locker_server.shared.utils.app import now, convert_readable_date


class EventService:
    """
    This class represents Use Cases related Event
    """

    def __init__(self, event_repository: EventRepository, user_repository: UserRepository):
        self.event_repository = event_repository
        self.user_repository = user_repository

    def list_events(self, **filters) -> List[Event]:
        return self.event_repository.list_events(**filters)

    def create_new_event(self, **data) -> Event:
        return self.event_repository.create_new_event(**data)

    def create_new_event_by_multiple_teams(self, team_ids: list, **data):
        return self.event_repository.create_new_event_by_multiple_teams(team_ids, **data)

    def create_new_event_by_ciphers(self, ciphers, **data):
        return self.event_repository.create_new_event_by_ciphers(ciphers, **data)

    def normalize_enterprise_activity(self, activity_logs: List[Event]) -> List[Event]:
        user_ids = [activity_log.user_id for activity_log in activity_logs if activity_log.user_id]
        acting_user_ids = [activity_log.acting_user_id for activity_log in activity_logs if activity_log.acting_user_id]
        query_user_ids = list(set(list(user_ids) + list(acting_user_ids)))
        users_data = self.user_repository.list_users(**{
            "user_ids": query_user_ids
        })
        users_data_dict = dict()
        for user_data in users_data:
            users_data_dict[user_data.user_id] = user_data
        for activity_log in activity_logs:
            acting_user_id = activity_log.acting_user_id
            user_id = activity_log.user_id
            acting_user_data = users_data_dict.get(acting_user_id)
            user_data = users_data_dict.get(user_id)
            activity_log.user = user_data
            activity_log.acting_user = acting_user_data
        return activity_logs

    def export_enterprise_activity(self, enterprise_member: EnterpriseMember, activity_logs,
                                   cc_emails=None, **kwargs) -> NoReturn:
        django_rq.enqueue(
            self.export_enterprise_activity_job, enterprise_member, activity_logs, cc_emails,
            kwargs.get("from"), kwargs.get("to")
        )

    def export_enterprise_activity_job(self, enterprise_member, activity_logs, cc_emails=None,
                                       from_param=None, to_param=None):
        current_time = now()
        filename = "activity_logs_{}".format(convert_readable_date(current_time, "%Y%m%d"))

        # Write to xlsx file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        title = ["Action", "Actor", "Time", "IP Address"]
        worksheet.write_row(0, 0, title)
        row_index = 2
        for log in activity_logs:
            row = [
                log.get("description", {}).get("en"),
                log.get("acting_user", {}).get("email") if log.get("acting_user") else "",
                convert_readable_date(log.get("creation_date")),
                log.get("ip_address")
            ]
            worksheet.write_row(row_index, 0, row)
            row_index += 1
        workbook.close()
        output.seek(0)

        # Upload to S3
        s3_path = f"support/tmp/activity/{enterprise_member.enterprise.enterprise_id}/{filename}.xlsx"
        # TODO: import s3_service
        s3_service.upload_bytes_object(key=s3_path, io_bytes=output)

        # Close IO Stream
        output.close()

        download_url = s3_service.gen_one_time_url(file_path=s3_path, **{"expired": 900})
        CyLog.debug(**{"message": f"Exported to {download_url}"})

        # Sending mail
        NotifyBackground(background=False).notify_enterprise_export(data={
            "user_ids": [enterprise_member.user.user_id],
            "cc": cc_emails,
            "attachments": [{
                "url": download_url,
                "name": f"{filename}.xlsx"
            }],
            "org_name": enterprise_member.enterprise.name,
            "start_date": from_param,
            "end_date": to_param
        })

    def statistic_login_by_time(self, enterprise_id: str, user_ids: List[int], from_param: float,
                                to_param: float) -> Dict:
        return self.event_repository.statistic_login_by_time(
            team_id=enterprise_id,
            user_ids=user_ids,
            from_param=from_param,
            to_param=to_param
        )
