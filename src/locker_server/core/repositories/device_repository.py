from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod


class DeviceRepository(ABC):
    # ------------------------ List Device resource ------------------- #

    # ------------------------ Get Device resource --------------------- #

    # ------------------------ Create Device resource --------------------- #

    # ------------------------ Update Device resource --------------------- #
    @abstractmethod
    def get_fcm_ids_by_user_ids(self, user_ids: List[int]) -> List[str]:
        pass

    # ------------------------ Delete Device resource --------------------- #
