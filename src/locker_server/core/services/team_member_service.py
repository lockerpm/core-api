from datetime import datetime
from typing import Optional, List, Dict

from locker_server.core.entities.member.team_member import TeamMember
from locker_server.core.entities.team.team import Team
from locker_server.core.exceptions.team_member_exception import TeamMemberDoesNotExistException
from locker_server.core.repositories.team_member_repository import TeamMemberRepository


class TeamMemberService:
    """
    This class represents Use Cases related TeamMember
    """

    def __init__(self, team_member_repository: TeamMemberRepository):
        self.team_member_repository = team_member_repository

    def list_member_user_ids_by_teams(self, teams: List[Team], status: str = None, personal_share: bool = None) -> List[int]:
        return self.team_member_repository.list_member_user_ids_by_teams(
            teams=teams, status=status, personal_share=personal_share
        )

    def get_team_member(self, user_id: int, team_id: str) -> Optional[TeamMember]:
        member = self.team_member_repository.get_user_team_member(user_id=user_id, team_id=team_id)
        if not member:
            raise TeamMemberDoesNotExistException
        return member

    def list_group_member_roles(self, team_member: TeamMember) -> List[str]:
        return self.team_member_repository.list_group_member_roles(team_member=team_member)

    def get_role_notify(self, user_id: int, team_id: str) -> Dict:
        return self.team_member_repository.get_role_notify_dict(team_id=team_id, user_id=user_id)
