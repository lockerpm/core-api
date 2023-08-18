from typing import Union, Dict, Optional
from abc import ABC, abstractmethod

from locker_server.core.entities.user.user import User


class EnterpriseMemberRepository(ABC):
    # ------------------------ List EnterpriseMember resource ------------------- #

    # ------------------------ Get EnterpriseMember resource --------------------- #

    # ------------------------ Create EnterpriseMember resource --------------------- #

    # ------------------------ Update EnterpriseMember resource --------------------- #
    @abstractmethod
    def enterprise_invitations_confirm(self, user: User, email: str = None) -> Optional[User]:
        pass

    @abstractmethod
    def enterprise_share_groups_confirm(self, user: User) -> Optional[User]:
        pass

    # ------------------------ Delete EnterpriseMember resource --------------------- #

