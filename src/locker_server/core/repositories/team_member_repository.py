from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.team.team import Team
from locker_server.core.entities.user.user import User


class TeamMemberRepository(ABC):
    # ------------------------ List TeamMember resource ------------------- #
    @abstractmethod
    def list_member_user_ids(self, team_ids: List[str], status: str = None, personal_share: bool = None) -> List[int]:
        pass

    @abstractmethod
    def list_member_user_ids_by_teams(self, teams: List[Team], status: str = None,
                                      personal_share: bool = None) -> List[int]:
        pass

    # ------------------------ Get TeamMember resource --------------------- #

    # ------------------------ Create TeamMember resource --------------------- #

    # ------------------------ Update TeamMember resource --------------------- #
    @abstractmethod
    def sharing_invitations_confirm(self, user: User, email: str = None) -> Optional[User]:
        pass

    # ------------------------ Delete TeamMember resource --------------------- #

