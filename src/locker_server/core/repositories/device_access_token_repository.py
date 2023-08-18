from typing import Union, Dict, Optional
from abc import ABC, abstractmethod

from locker_server.core.entities.user.device_access_token import DeviceAccessToken


class DeviceAccessTokenRepository(ABC):
    # ------------------------ List DeviceAccessToken resource ------------------- #

    # ------------------------ Get DeviceAccessToken resource --------------------- #
    @abstractmethod
    def get_device_access_token_by_id(self, device_access_token_id: str) -> Optional[DeviceAccessToken]:
        pass

    # ------------------------ Create DeviceAccessToken resource --------------------- #

    # ------------------------ Update DeviceAccessToken resource --------------------- #

    # ------------------------ Delete DeviceAccessToken resource --------------------- #

