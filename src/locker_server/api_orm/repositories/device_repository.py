from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_device_model
from locker_server.core.entities.user.device import Device
from locker_server.core.repositories.device_repository import DeviceRepository
from locker_server.shared.utils.app import now

DeviceORM = get_device_model()
ModelParser = get_model_parser()


class DeviceORMRepository(DeviceRepository):
    # ------------------------ List Device resource ------------------- #
    def list_user_devices(self, user_id: int, **filter_params) -> List[Device]:
        devices_orm = DeviceORM.objects.filter(user_id=user_id).select_related('user').order_by('-created_time')
        return [ModelParser.user_parser().parse_device(device_orm=device_orm) for device_orm in devices_orm]

    # ------------------------ Get Device resource --------------------- #
    def get_device_by_identifier(self, user_id: int, device_identifier: str) -> Optional[Device]:
        try:
            device_orm = DeviceORM.objects.get(user_id=user_id, device_identifier=device_identifier)
            return ModelParser.user_parser().parse_device(device_orm=device_orm)
        except DeviceORM.DoesNotExist:
            return None

    # ------------------------ Create Device resource --------------------- #
    def retrieve_or_create(self, user_id: int, **data) -> Device:
        device_orm = DeviceORM.retrieve_or_create(user_id=user_id, **data)
        return ModelParser.user_parser().parse_device(device_orm=device_orm)

    # ------------------------ Update Device resource --------------------- #
    def get_fcm_ids_by_user_ids(self, user_ids: List[int]) -> List[str]:
        fcm_ids = DeviceORM.objects.filter(
            user_id__in=user_ids
        ).exclude(fcm_id__isnull=True).exclude(fcm_id="").values_list('fcm_id', flat=True)
        return list(set(fcm_ids))

    def set_last_login(self, device_id: int, last_login: float) -> Device:
        try:
            device_orm = DeviceORM.objects.get(id=device_id)
            device_orm.last_login = last_login or now()
            return ModelParser.user_parser().parse_device(device_orm=device_orm)
        except DeviceORM.DoesNotExist:
            return

    def update_fcm_id(self, user_id: int, device_identifier: str, fcm_id: str) -> Device:
        try:
            device_orm = DeviceORM.objects.get(user_id=user_id, device_identifier=device_identifier)
            device_orm.fcm_id = fcm_id
            device_orm.save()
            return ModelParser.user_parser().parse_device(device_orm=device_orm)
        except DeviceORM.DoesNotExist:
            return None


    # ------------------------ Delete Device resource --------------------- #
