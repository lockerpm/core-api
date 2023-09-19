from typing import Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.notification.notification_setting import NotificationSetting


class NotificationSettingRepository(ABC):
    # ------------------------ List NotificationSetting resource ------------------- #

    # ------------------------ Get NotificationSetting resource --------------------- #
    @abstractmethod
    def get_user_notification(self, category_id: str, user_ids: List[int], is_notify: bool = True) -> List[int]:
        pass

    @abstractmethod
    def get_user_mail(self, category_id: str, user_ids: List[int], is_notify: bool = True) -> List[int]:
        pass

    # ------------------------ Create NotificationSetting resource --------------------- #

    # ------------------------ Update NotificationSetting resource --------------------- #

    # ------------------------ Delete NotificationSetting resource --------------------- #
