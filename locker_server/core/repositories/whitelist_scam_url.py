from typing import Optional, List, NoReturn, Dict
from abc import ABC, abstractmethod

from locker_server.core.entities.scam_setting.whitelist_scam_url import WhitelistScamUrl


class WhitelistScamUrlRepository(ABC):
    # ------------------------ List WhitelistScamUrl resource ------------------- #
    @abstractmethod
    def list_wl_scam_urls(self, user_id: int, **filters) -> List[WhitelistScamUrl]:
        pass

    # ------------------------ Get WhitelistScamUrl resource --------------------- #
    @abstractmethod
    def get_wl_scam_url_by_id(self, wl_scam_url_id: str) -> List[int]:
        pass

    @abstractmethod
    def get_by_url(self, user_id, url) -> Optional[WhitelistScamUrl]:
        pass

    # ------------------------ Create WhitelistScamUrl resource --------------------- #
    @abstractmethod
    def create_wl_scam_url(self, **create_data) -> WhitelistScamUrl:
        pass

    # ------------------------ Update WhitelistScamUrl resource --------------------- #
    @abstractmethod
    def update_wl_scam_url(self, wl_scam_url_id: str, **scam_update_data) \
            -> Optional[WhitelistScamUrl]:
        pass

    # ------------------------ Delete WhitelistScamUrl resource --------------------- #
    @abstractmethod
    def delete_wl_scam_url(self, wl_scam_url_id: str) -> bool:
        pass
