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

    @abstractmethod
    def is_block_by_2fa_policy(self, user_id: int, is_factor2: bool) -> bool:
        pass

    @abstractmethod
    def count_failed_login_event(self, user_id: int) -> int:
        pass

    @abstractmethod
    def has_master_pw_item(self, user_id: int) -> bool:
        pass

    # ------------------------ Create User resource --------------------- #
    @abstractmethod
    def retrieve_or_create_by_id(self, user_id, creation_date=None) -> Tuple[User, bool]:
        pass

    # ------------------------ Update User resource --------------------- #
    @abstractmethod
    def update_user(self, user_id: int, user_update_data) -> Optional[User]:
        pass

    @abstractmethod
    def update_login_time_user(self, user_id: int, update_data) -> Optional[User]:
        pass

    @abstractmethod
    def update_passwordless_cred(self, user_id: int, fd_credential_id: str, fd_random: str) -> User:
        pass

    @abstractmethod
    def change_master_password(self, user: User, new_master_password_hash: str, new_master_password_hint: str = None,
                               key: str = None, score=None, login_method: str = None):
        pass

    # ------------------------ Delete User resource --------------------- #
    @abstractmethod
    def purge_account(self, user: User):
        pass

    @abstractmethod
    def delete_account(self, user: User):
        pass

    @abstractmethod
    def revoke_all_sessions(self, user: User, exclude_sso_token_ids=None) -> User:
        pass
