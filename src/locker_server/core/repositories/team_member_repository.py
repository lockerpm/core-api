from typing import Union, Dict, Optional
from abc import ABC, abstractmethod

from locker_server.core.entities.user.user import User


class TeamMemberRepository(ABC):
    # ------------------------ List TeamMember resource ------------------- #

    # ------------------------ Get TeamMember resource --------------------- #

    # ------------------------ Create TeamMember resource --------------------- #

    # ------------------------ Update TeamMember resource --------------------- #
    @abstractmethod
    def sharing_invitations_confirm(self, user: User, email: str = None) -> Optional[User]:
        pass

    # ------------------------ Delete TeamMember resource --------------------- #

