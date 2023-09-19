from typing import Optional, List
from abc import ABC, abstractmethod

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_notification_setting_model
from locker_server.core.entities.notification.notification_setting import NotificationSetting
from locker_server.core.repositories.notification_setting_repository import NotificationSettingRepository
from locker_server.shared.utils.app import diff_list


NotificationSettingORM = get_notification_setting_model()
ModelParser = get_model_parser()


class NotificationSettingORMRepository(NotificationSettingRepository):
    # ------------------------ List NotificationSetting resource ------------------- #

    # ------------------------ Get NotificationSetting resource --------------------- #
    def get_user_notification(self, category_id: str, user_ids: List[int], is_notify: bool = True) -> List[int]:
        exist_user_notifications = NotificationSettingORM.objects.filter(user_id__in=user_ids, category_id=category_id)
        # Get non-exist user notification settings => The default value is True
        non_exist_user_notifications = diff_list(
            user_ids, list(exist_user_notifications.values_list('user_id', flat=True))
        )
        # Get list user_ids turn on/off notification
        notifications = list(
            exist_user_notifications.filter(notification=is_notify).values_list('user_id', flat=True)
        )
        # If we get list turn on, the returned result is non_exist_user_notifications and turn_on_notification
        return list(set(non_exist_user_notifications + notifications)) if is_notify is True else notifications

    def get_user_mail(self, category_id: str, user_ids: List[int], is_notify: bool = True) -> List[int]:
        exist_user_notifications = NotificationSettingORM.objects.filter(user_id__in=user_ids, category_id=category_id)
        # Get non-exist user notifications => The default value is True
        non_exist_user_notifications = diff_list(
            user_ids, list(exist_user_notifications.values_list('user_id', flat=True))
        )
        # Get list user_ids turn on/off mail
        mails = list(
            exist_user_notifications.filter(mail=is_notify).values_list('user_id', flat=True)
        )

        # If we get list mail turn on, the returned result is non_exist_user_notifications and mail on
        return non_exist_user_notifications + mails if is_notify is True else mails

    # ------------------------ Create NotificationSetting resource --------------------- #

    # ------------------------ Update NotificationSetting resource --------------------- #

    # ------------------------ Delete NotificationSetting resource --------------------- #
