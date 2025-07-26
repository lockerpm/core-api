from typing import List

from locker_server.core.entities.scam_setting.scam_setting import ScamSetting
from locker_server.core.repositories.user_scam_setting_repository import ScamSettingRepository
from locker_server.shared.constants.scam_setting import LIST_SCAM_SETTING_CATEGORIES


class ScamSettingService:
    """
    This class represents Use Cases related scam settings
    """

    def __init__(self, scam_setting_repository: ScamSettingRepository):
        self.scam_setting_repository = scam_setting_repository

    def list_user_scam_settings(self, user_id: str, **filters) -> List[ScamSetting]:
        current_setting = self.scam_setting_repository.list_user_scam_settings(user_id, **filters)

        if len(current_setting) < len(LIST_SCAM_SETTING_CATEGORIES):
            list_create_data = []

            current_dict = {s.category.scam_setting_category_id: s for s in current_setting}
            for key in LIST_SCAM_SETTING_CATEGORIES:
                existed = current_dict.get(key)
                if existed:
                    continue
                # Add new setting for user
                list_create_data.append({
                    "category_id": key,
                    "enabled": True,
                    "user_id": user_id,
                })
            self.scam_setting_repository.create_multiple_scam_setting(user_id, list_create_data)
            return self.scam_setting_repository.list_user_scam_settings(user_id, **filters)
        return current_setting

    def create_multiple_scam_setting(self, user_id: str, list_create_data):
        return self.scam_setting_repository.create_multiple_scam_setting(user_id, list_create_data)
