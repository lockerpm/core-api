from typing import Optional, List, Dict

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.core.entities.factor2.device_factor2 import DeviceFactor2
from locker_server.api_orm.models.factor2.device_factor2 import DeviceFactor2ORM
from locker_server.core.repositories.device_factor2_repository import DeviceFactor2Repository
from locker_server.shared.utils.app import now

DeviceFactor2ORM = DeviceFactor2ORM
ModelParser = get_model_parser()


class DeviceFactor2ORMRepository(DeviceFactor2Repository):
    # ------------------------ List DeviceFactor2 resource ------------------- #
    def list_user_device_factor2s(self, user_id: int, **filter_params) -> List[DeviceFactor2]:
        pass

    # ------------------------ Get DeviceFactor2 resource --------------------- #
    def get_device_factor2_by_id(self, device_factor2_id: str) -> Optional[DeviceFactor2]:
        pass

    def get_device_factor2_by_method(self, user_id: int, method: str) -> DeviceFactor2:
        pass

    def get_device_factor2_by_device_id(self, device_id: int) -> Optional[DeviceFactor2]:
        # Delete all expired device factor2
        expired_device_factor2_orm = DeviceFactor2ORM.objects.filter(
            expired_time__lte=now()
        )
        expired_device_factor2_orm.delete()

        device_factor2_orm = DeviceFactor2ORM.objects.filter(
            device_id=device_id
        ).first()
        if not device_factor2_orm:
            return None
        return ModelParser.factor2_parser().parse_device_factor2(
            device_factor2_orm=device_factor2_orm
        )

    # ------------------------ Create DeviceFactor2 resource --------------------- #
    def create_device_factor2(self, device_factor2_create_data: Dict) -> DeviceFactor2:
        factor2_method_id = device_factor2_create_data.get("factor2_method_id")
        device_id = device_factor2_create_data.get("device_id")
        device_factor2_orm = DeviceFactor2ORM.create(
            device_id=device_id,
            factor2_method_id=factor2_method_id
        )
        return ModelParser.factor2_parser().parse_device_factor2(
            device_factor2_orm=device_factor2_orm
        )

    # ------------------------ Update DeviceFactor2 resource --------------------- #

    # ------------------------ Delete DeviceFactor2 resource --------------------- #
    def delete_device_factor2_by_user_id(self, user_id: int):
        device_factor2_orm = DeviceFactor2ORM.objects.filter(
            factor2_method__user_id=user_id
        )
        device_factor2_orm.delete()
