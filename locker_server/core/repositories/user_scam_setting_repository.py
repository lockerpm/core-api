from typing import Optional, List, NoReturn, Dict
from abc import ABC, abstractmethod

from locker_server.core.entities.scam_setting.scam_setting import ScamSetting


class ScamSettingRepository(ABC):
    # ------------------------ List ScamSetting resource ------------------- #
    @abstractmethod
    def list_user_scam_settings(self, user_id: int, **filters) -> List[ScamSetting]:
        pass

    @abstractmethod
    def check_user_scam_settings(self, user_id: int) -> bool:
        pass

    # ------------------------ Get ScamSetting resource --------------------- #
    @abstractmethod
    def get_user_scam_setting(self, category_id: str, user_ids: List[int]) -> List[int]:
        pass

    @abstractmethod
    def get_user_mail(self, category_id: str, user_ids: List[int]) -> List[int]:
        pass

    @abstractmethod
    def get_user_scam_by_category_id(self, user_id: int, category_id: str) -> Optional[ScamSetting]:
        pass

    # ------------------------ Create ScamSetting resource --------------------- #
    @abstractmethod
    def create_multiple_scam_setting(self, user_id: str, list_create_data: List[Dict]) -> NoReturn:
        pass

    # ------------------------ Update ScamSetting resource --------------------- #
    @abstractmethod
    def update_scam_setting(self, scam_setting_id: str, scam_update_data) \
            -> Optional[ScamSetting]:
        pass
    # ------------------------ Delete ScamSetting resource --------------------- #
