from typing import Optional, List, Dict
from abc import ABC, abstractmethod

from locker_server.core.entities.configuration.app_info import AppInfo


class AppInfoRepository(ABC):
    # ------------------------ List AppInfo resource ------------------- #

    # ------------------------ Get AppInfo resource --------------------- #
    @abstractmethod
    def get_app_info(self) -> Optional[AppInfo]:
        pass

    @abstractmethod
    def get_app_logo(self) -> Optional[str]:
        pass

    # ------------------------ Create MailConfiguration resource --------------------- #

    # ------------------------ Update MailConfiguration resource --------------------- #
    @abstractmethod
    def update_logo(self, new_logo) -> str:
        pass

    @abstractmethod
    def update_app_info(self, update_data: Dict) -> AppInfo:
        pass

    # ------------------------ Delete MailConfiguration resource --------------------- #
