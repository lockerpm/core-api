from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from django.db.models import Count, Case, When

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_device_model, get_device_access_token_model
from locker_server.core.entities.user.device import Device
from locker_server.core.repositories.device_repository import DeviceRepository
from locker_server.shared.constants.device_type import *
from locker_server.shared.utils.app import now

DeviceORM = get_device_model()
DeviceAccessTokenORM = get_device_access_token_model()
ModelParser = get_model_parser()


class DeviceORMRepository(DeviceRepository):
    # ------------------------ List Device resource ------------------- #
    def list_user_devices(self, user_id: int, **filter_params) -> List[Device]:
        devices_orm = DeviceORM.objects.filter(user_id=user_id).select_related('user').order_by('-created_time')
        return [ModelParser.user_parser().parse_device(device_orm=device_orm) for device_orm in devices_orm]

    def list_devices(self, **filter_params) -> List[Device]:
        devices_orm = DeviceORM.objects.all().order_by('-created_time')
        user_id_param = filter_params.get("user_id")
        client_id_param = filter_params.get("client_id")
        device_identifier_param = filter_params.get("device_identifier")

        if user_id_param:
            devices_orm = devices_orm.filter(user_id=user_id_param)
        if client_id_param:
            devices_orm = devices_orm.filter(client_id=client_id_param)
        if device_identifier_param:
            devices_orm = devices_orm.filter(device_identifier=device_identifier_param)
        devices_orm = devices_orm.select_related('user')
        return [ModelParser.user_parser().parse_device(device_orm=device_orm) for device_orm in devices_orm]

    # ------------------------ Get Device resource --------------------- #
    def get_device_by_identifier(self, user_id: int, device_identifier: str) -> Optional[Device]:
        try:
            device_orm = DeviceORM.objects.get(user_id=user_id, device_identifier=device_identifier)
            return ModelParser.user_parser().parse_device(device_orm=device_orm)
        except DeviceORM.DoesNotExist:
            return None

    def get_fcm_ids_by_user_ids(self, user_ids: List[int]) -> List[str]:
        fcm_ids = DeviceORM.objects.filter(
            user_id__in=user_ids
        ).exclude(fcm_id__isnull=True).exclude(fcm_id="").values_list('fcm_id', flat=True)
        return list(set(fcm_ids))

    def is_active(self, device_id) -> bool:
        return DeviceAccessTokenORM.objects.filter(device_id=device_id).exists()

    def statistic_multiple_device_by_user_id(self, user_id) -> Dict:
        devices_orm = DeviceORM.objects.filter(user_id=user_id)
        web_device_count = devices_orm.filter(
            client_id=CLIENT_ID_WEB
        ).count()
        mobile_device_count = devices_orm.filter(
            client_id=CLIENT_ID_MOBILE
        ).count()
        ios_device_count = devices_orm.filter(
            device_type=DEVICE_TYPE_IOS
        ).count()
        android_device_count = devices_orm.filter(
            device_type=DEVICE_TYPE_ANDROID
        ).count()
        extension_device_count = devices_orm.filter(
            client_id=CLIENT_ID_BROWSER
        ).count()
        desktop_device_count = devices_orm.filter(
            client_id=CLIENT_ID_DESKTOP
        ).count()
        desktop_windows_count = devices_orm.filter(
            client_id=CLIENT_ID_DESKTOP,
            device_type=DEVICE_TYPE_WINDOWS
        ).count()
        desktop_linux_count = devices_orm.filter(
            client_id=CLIENT_ID_DESKTOP,
            device_type=DEVICE_TYPE_LINUX
        ).count()
        desktop_mac_count = devices_orm.filter(
            client_id=CLIENT_ID_DESKTOP,
            device_type=DEVICE_TYPE_MAC
        ).count()

        return {
            "mobile": mobile_device_count,
            "android": android_device_count,
            "ios": ios_device_count,
            "web": web_device_count,
            "browser": extension_device_count,
            "desktop": desktop_device_count,
            "desktop_windows": desktop_windows_count,
            "desktop_linux": desktop_linux_count,
            "desktop_mac": desktop_mac_count,
        }

    # ------------------------ Create Device resource --------------------- #
    def retrieve_or_create(self, user_id: int, **data) -> Device:
        device_orm = DeviceORM.retrieve_or_create(user_id=user_id, **data)
        return ModelParser.user_parser().parse_device(device_orm=device_orm)

    # ------------------------ Update Device resource --------------------- #
    def set_last_login(self, device_id: int, last_login: float) -> Device:
        try:
            device_orm = DeviceORM.objects.get(id=device_id)
            device_orm.last_login = last_login or now()
            return ModelParser.user_parser().parse_device(device_orm=device_orm)
        except DeviceORM.DoesNotExist:
            return

    def update_fcm_id(self, user_id: int, device_identifier: str, fcm_id: str) -> Optional[Device]:
        try:
            device_orm = DeviceORM.objects.get(user_id=user_id, device_identifier=device_identifier)
            device_orm.fcm_id = fcm_id
            device_orm.save()
            return ModelParser.user_parser().parse_device(device_orm=device_orm)
        except DeviceORM.DoesNotExist:
            return None

    def update_auto_verify(self, user_id: int, device_identifier: str, h: str, p: str) -> Optional[Device]:
        try:
            device_orm = DeviceORM.objects.get(device_identifier=device_identifier, user_id=user_id)
            device_orm.h = h
            device_orm.p = p
            device_orm.save()
            return ModelParser.user_parser().parse_device(device_orm=device_orm)
        except DeviceORM.DoesNotExist:
            return None

    # ------------------------ Delete Device resource --------------------- #
    def destroy_device(self, device: Device) -> List[str]:
        try:
            device_orm = DeviceORM.objects.get(id=device.device_id)
        except DeviceORM.DoesNotExist:
            return None
        sso_token_ids = list(device_orm.device_access_tokens.values_list('sso_token_id', flat=True))
        device_orm.delete()
        return sso_token_ids
