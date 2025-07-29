from typing import List

from locker_server.core.entities.scam_setting.scam_setting import ScamSetting
from locker_server.core.entities.scam_setting.whitelist_scam_url import WhitelistScamUrl
from locker_server.core.exceptions.whitelist_scam_url_exception import WhitelistScamUrlDoesNotExistException, \
    WhitelistScamUrlExistedException
from locker_server.core.repositories.user_scam_setting_repository import ScamSettingRepository
from locker_server.core.repositories.whitelist_scam_url import WhitelistScamUrlRepository
from locker_server.shared.constants.scam_setting import LIST_SCAM_SETTING_CATEGORIES


class ScamSettingService:
    """
    This class represents Use Cases related scam settings
    """

    def __init__(self, scam_setting_repository: ScamSettingRepository,
                 whitelist_scam_url_repository: WhitelistScamUrlRepository):
        self.scam_setting_repository = scam_setting_repository
        self.whitelist_scam_url_repository = whitelist_scam_url_repository

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

    def list_wl_scam_urls(self, **filters) -> List[WhitelistScamUrl]:
        return self.whitelist_scam_url_repository.list_wl_scam_urls(**filters)

    def create_wl_scam_url(self, **create_data) -> WhitelistScamUrl:
        return self.whitelist_scam_url_repository.create_wl_scam_url(**create_data)

    def update_wl_scam_url(self, user_id: str, wl_url_id: str, **update_data) -> WhitelistScamUrl:
        url = update_data.get("url")
        existed_orm = self.whitelist_scam_url_repository.get_by_url(
            user_id=user_id,
            url=url
        )
        if existed_orm and existed_orm.whitelist_scam_url_id != wl_url_id:
            raise WhitelistScamUrlExistedException

        updated_wl_url = self.whitelist_scam_url_repository.update_wl_scam_url(wl_url_id, **update_data)
        if not updated_wl_url:
            raise WhitelistScamUrlDoesNotExistException
        return updated_wl_url

    def delete_wl_scam_url(self, wl_url_id: str) -> bool:
        return self.whitelist_scam_url_repository.delete_wl_scam_url(wl_url_id)

    def get_wl_scam_url(self, wl_url_id: str) -> WhitelistScamUrl:
        wl_scam_url = self.whitelist_scam_url_repository.get_wl_scam_url_by_id(wl_url_id)
        if not wl_scam_url:
            raise WhitelistScamUrlDoesNotExistException
        return wl_scam_url
