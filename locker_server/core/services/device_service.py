from typing import List

from locker_server.core.entities.user.device import Device
from locker_server.core.repositories.device_repository import DeviceRepository


class DeviceService:
    """
    This class represents Use Cases related Device
    """
    def __init__(self, device_repository: DeviceRepository):
        self.device_repository = device_repository

    def list_devices(self, **filter_params) -> List[Device]:
        return self.device_repository.list_devices(**filter_params)
