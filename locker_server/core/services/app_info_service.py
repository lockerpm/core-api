from typing import Optional

from locker_server.core.entities.configuration.app_info import AppInfo
from locker_server.core.repositories.app_info_repository import AppInfoRepository


class AppInfoService:
    def __init__(self, app_info_repository: AppInfoRepository):
        self.app_info_repository = app_info_repository

    def get_app_info(self) -> Optional[AppInfo]:
        return self.app_info_repository.get_app_info()

    def update_app_info(self, update_data) -> AppInfo:
        return self.app_info_repository.update_app_info(
            update_data=update_data
        )

    def get_app_logo(self) -> Optional[str]:
        return self.app_info_repository.get_app_logo()

    def update_app_logo(self, new_logo) -> str:
        return self.app_info_repository.update_logo(
            new_logo=new_logo
        )
