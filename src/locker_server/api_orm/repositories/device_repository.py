from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_device_model
from locker_server.core.repositories.device_repository import DeviceRepository


DeviceORM = get_device_model()
ModelParser = get_model_parser()


class DeviceORMRepository(DeviceRepository):
    # ------------------------ List Device resource ------------------- #

    # ------------------------ Get Device resource --------------------- #

    # ------------------------ Create Device resource --------------------- #

    # ------------------------ Update Device resource --------------------- #
    def get_fcm_ids_by_user_ids(self, user_ids: List[int]) -> List[str]:
        fcm_ids = DeviceORM.objects.filter(
            user_id__in=user_ids
        ).exclude(fcm_id__isnull=True).exclude(fcm_id="").values_list('fcm_id', flat=True)
        return list(set(fcm_ids))

    # ------------------------ Delete Device resource --------------------- #
