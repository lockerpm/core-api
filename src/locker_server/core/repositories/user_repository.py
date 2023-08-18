from typing import Union, Dict, Optional, Tuple
from abc import ABC, abstractmethod

from locker_server.core.entities.user.user import User
from locker_server.core.entities.user.user_score import UserScore
from locker_server.shared.constants.enterprise_members import E_MEMBER_STATUS_CONFIRMED


class UserRepository(ABC):
    # ------------------------ List User resource ------------------- #

    # ------------------------ Get User resource --------------------- #
    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_user_type(self, user_id: int) -> str:
        pass

    @abstractmethod
    def is_in_enterprise(self, user_id: int) -> bool:
        pass

    @abstractmethod
    def is_require_passwordless(self, user_id: int,
                                require_enterprise_member_status: str = E_MEMBER_STATUS_CONFIRMED) -> bool:
        pass

    # ------------------------ Create User resource --------------------- #
    @abstractmethod
    def retrieve_or_create_by_id(self, user_id, creation_date=None) -> Tuple[User, bool]:
        pass

    # ------------------------ Update User resource --------------------- #
    @abstractmethod
    def update_user(self, user_id: int, user_update_data) -> Optional[User]:
        pass

    # ------------------------ Delete User resource --------------------- #

