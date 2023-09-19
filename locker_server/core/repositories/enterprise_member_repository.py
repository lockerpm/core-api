from typing import Union, Dict, Optional
from abc import ABC, abstractmethod

from locker_server.core.entities.enterprise.member.enterprise_member import EnterpriseMember
from locker_server.core.entities.user.user import User


class EnterpriseMemberRepository(ABC):
    # ------------------------ List EnterpriseMember resource ------------------- #

    # ------------------------ Get EnterpriseMember resource --------------------- #
    @abstractmethod
    def get_primary_member(self, enterprise_id: str) -> Optional[EnterpriseMember]:
        pass

    @abstractmethod
    def get_enterprise_member_by_user_id(self, enterprise_id: str, user_id: int) -> Optional[EnterpriseMember]:
        pass

    @abstractmethod
    def lock_login_account_belong_enterprise(self, user_id: int) -> bool:
        pass

    @abstractmethod
    def is_active_enterprise_member(self, user_id: int) -> bool:
        pass

    # ------------------------ Create EnterpriseMember resource --------------------- #

    # ------------------------ Update EnterpriseMember resource --------------------- #
    @abstractmethod
    def enterprise_invitations_confirm(self, user: User, email: str = None) -> Optional[User]:
        pass

    @abstractmethod
    def enterprise_share_groups_confirm(self, user: User) -> Optional[User]:
        pass

    # ------------------------ Delete EnterpriseMember resource --------------------- #

