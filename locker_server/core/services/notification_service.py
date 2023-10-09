from typing import List, Optional, NoReturn, Dict
from datetime import datetime

import pyotp

from locker_server.core.entities.factor2.factor2_method import Factor2Method
from locker_server.core.entities.notification.notification import Notification
from locker_server.core.entities.user.user import User
from locker_server.core.exceptions.factor2_method_exception import Factor2CodeInvalidException, \
    Factor2MethodInvalidException
from locker_server.core.exceptions.notification_exception import NotificationDoesNotExistException
from locker_server.core.exceptions.user_exception import UserDoesNotExistException, UserPasswordInvalidException
from locker_server.core.repositories.auth_repository import AuthRepository

from locker_server.core.repositories.factor2_method_repository import Factor2MethodRepository
from locker_server.core.repositories.notification_repository import NotificationRepository
from locker_server.core.repositories.user_repository import UserRepository
from locker_server.shared.constants.factor2 import FA2_METHOD_MAIL_OTP, LIST_FA2_METHOD, FA2_METHOD_SMART_OTP
from locker_server.shared.constants.user_notification import ID_FACTOR2_MAIL_LOGIN, ID_FACTOR2_ENABLED_SUCCESSFULLY, \
    ID_FACTOR2_DISABLED, ID_FACTOR2_ENABLED, ID_FACTOR2_DISABLED_SUCCESSFULLY
from locker_server.shared.external_services.locker_background.constants import BG_NOTIFY
from locker_server.shared.utils.app import get_ip_location, now


class NotificationService:
    """
    This class represents Use Cases related User
    """

    def __init__(self, notification_repository: NotificationRepository,
                 user_repository: UserRepository,
                 ):
        self.user_repository = user_repository
        self.notification_repository = notification_repository

    def list_notifications(self, **filters) -> List[Notification]:
        return self.notification_repository.list_notifications(**filters)

    def count_notifications(self, **filters) -> int:
        return self.notification_repository.count_notifications(**filters)

    def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        notification = self.notification_repository.get_notification_by_id(
            notification_id=notification_id
        )
        if not notification:
            raise NotificationDoesNotExistException
        return notification

    def update_notification(self, notification_id: str, read: bool, clicked=None):
        updated_notification = self.notification_repository.update_notification(
            notification_id=notification_id,
            read=read,
            clicked=clicked
        )
        if not updated_notification:
            raise NotificationDoesNotExistException
        return updated_notification

    def read_all(self, **filters):
        self.notification_repository.read_all(**filters)
