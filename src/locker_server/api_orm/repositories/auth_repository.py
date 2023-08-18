from typing import Union, Optional, Dict
import jwt

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_user_model
from locker_server.core.repositories.auth_repository import AuthRepository
from locker_server.shared.constants.token import *
from locker_server.shared.utils.app import now

UserORM = get_user_model()
ModelParser = get_model_parser()


class AuthORMRepository(AuthRepository):
    def decode_token(self, value: str, secret: str) -> Dict:
        if value.startswith(TOKEN_PREFIX):
            value = value[len(TOKEN_PREFIX):]
        try:
            payload = jwt.decode(value, secret, algorithms=['HS256'])
            return payload
        except (jwt.InvalidSignatureError, jwt.DecodeError, jwt.InvalidAlgorithmError):
            return None

    def get_expired_type(self, token_type_name: str) -> Union[int, float]:
        if token_type_name == TOKEN_TYPE_AUTHENTICATION:
            return now() + TOKEN_EXPIRED_TIME_AUTHENTICATION * 3600
        return 0
