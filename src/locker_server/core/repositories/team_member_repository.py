from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.member.team_member import TeamMember
from locker_server.core.entities.team.team import Team
from locker_server.core.entities.user.user import User


class TeamMemberRepository(ABC):
    # ------------------------ List TeamMember resource ------------------- #
    @abstractmethod
    def list_members_by_user_id(self, user_id: int, **filter_params) -> List[TeamMember]:
        pass

    @abstractmethod
    def list_member_user_ids(self, team_ids: List[str], status: str = None, personal_share: bool = None) -> List[int]:
        pass

    @abstractmethod
    def list_member_user_ids_by_teams(self, teams: List[Team], status: str = None,
                                      personal_share: bool = None) -> List[int]:
        pass

    @abstractmethod
    def list_group_member_roles(self, team_member: TeamMember) -> List[str]:
        pass

    @abstractmethod
    def list_member_collection_ids(self, team_member_id: int) -> List[str]:
        pass

    @abstractmethod
    def list_team_ids_owner_family_plan(self, user_id: int) -> List[str]:
        pass

    # ------------------------ Get TeamMember resource --------------------- #
    @abstractmethod
    def get_team_member_by_id(self, team_member_id: int) -> Optional[TeamMember]:
        pass

    @abstractmethod
    def get_user_team_member(self, user_id: int, team_id: str) -> Optional[TeamMember]:
        pass

    @abstractmethod
    def get_primary_member(self, team_id: str) -> Optional[TeamMember]:
        pass

    @abstractmethod
    def get_role_notify_dict(self, team_id: str, user_id: int) -> Dict:
        pass

    # ------------------------ Create TeamMember resource --------------------- #

    # ------------------------ Update TeamMember resource --------------------- #
    @abstractmethod
    def sharing_invitations_confirm(self, user: User, email: str = None) -> Optional[User]:
        pass

    @abstractmethod
    def reject_invitation(self, team_member_id: int):
        pass

    @abstractmethod
    def confirm_invitation(self, team_member_id: int, key: str) -> Optional[TeamMember]:
        pass

    @abstractmethod
    def accept_invitation(self, team_member_id: int) -> Optional[TeamMember]:
        pass

    # ------------------------ Delete TeamMember resource --------------------- #

