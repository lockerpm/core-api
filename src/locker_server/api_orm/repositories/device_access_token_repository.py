from typing import Optional

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_device_access_token_model
from locker_server.core.entities.user.device_access_token import DeviceAccessToken
from locker_server.core.repositories.device_access_token_repository import DeviceAccessTokenRepository


DeviceAccessTokenORM = get_device_access_token_model()
ModelParser = get_model_parser()


class DeviceAccessTokenORMRepository(DeviceAccessTokenRepository):
    # ------------------------ List DeviceAccessToken resource ------------------- #

    # ------------------------ Get DeviceAccessToken resource --------------------- #
    def get_device_access_token_by_id(self, device_access_token_id: str) -> Optional[DeviceAccessToken]:
        try:
            device_access_token_orm = DeviceAccessTokenORM.objects.get(id=device_access_token_id)
        except DeviceAccessTokenORM.DoesNotExist:
            return None
        return ModelParser.user_parser().parse_device_access_token(device_access_token_orm=device_access_token_orm)

    # ------------------------ Create DeviceAccessToken resource --------------------- #

    # ------------------------ Update DeviceAccessToken resource --------------------- #

    # ------------------------ Delete DeviceAccessToken resource --------------------- #

