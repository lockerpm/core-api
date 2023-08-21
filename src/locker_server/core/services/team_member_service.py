from datetime import datetime
from typing import Optional, List

from locker_server.core.entities.team.team import Team
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
