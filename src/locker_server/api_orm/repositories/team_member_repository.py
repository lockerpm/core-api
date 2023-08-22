from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_user_model, get_team_member_model, get_group_member_model, \
    get_collection_member_model
from locker_server.core.entities.member.team_member import TeamMember
from locker_server.core.entities.team.team import Team
from locker_server.core.entities.user.user import User
from locker_server.core.repositories.team_member_repository import TeamMemberRepository
from locker_server.shared.constants.members import PM_MEMBER_STATUS_INVITED

UserORM = get_user_model()
TeamMemberORM = get_team_member_model()
GroupMemberORM = get_group_member_model()
CollectionMemberORM = get_collection_member_model()
# PMPlanORM = get_plan_model()
# PMUserPlanORM = get_user_plan_model()
# EnterpriseMemberRoleORM = get_enterprise_member_role_model()
# EnterpriseMemberORM = get_enterprise_member_model()
# EnterpriseORM = get_enterprise_model()
ModelParser = get_model_parser()


class TeamMemberORMRepository(TeamMemberRepository):
    @staticmethod
    def _get_user_orm(user_id: int) -> Optional[UserORM]:
        try:
            return UserORM.objects.get(id=user_id)
        except UserORM.DoesNotExist:
            return None

    # ------------------------ List TeamMember resource ------------------- #
    def list_member_user_ids(self, team_ids: List[str], status: str = None, personal_share: bool = None) -> List[int]:
        members_orm = TeamMemberORM.objects.filter(team_id__in=team_ids)
        if status is not None:
            members_orm = members_orm.filter(status=status)
        if personal_share is not None:
            members_orm = members_orm.filter(team__personal_share=personal_share)
        return list(members_orm.values_list('user_id', flat=True))

    def list_member_user_ids_by_teams(self, teams: List[Team], status: str = None,
                                      personal_share: bool = None) -> List[int]:
        team_ids = [team.team_id for team in teams]
        return self.list_member_user_ids(team_ids=team_ids, status=status, personal_share=personal_share)

    def list_group_member_roles(self, team_member: TeamMember) -> List[str]:
        return list(GroupMemberORM.objects.filter(
            member_id=team_member.team_member_id
        ).values_list('group__role_id', flat=True))

    def list_member_collection_ids(self, team_member_id: int) -> List[str]:
        return list(
            CollectionMemberORM.objects.filter(member_id=team_member_id).values_list('collection_id', flat=True)
        )

    # ------------------------ Get TeamMember resource --------------------- #
    def get_user_team_member(self, user_id: int, team_id: str) -> Optional[TeamMember]:
        try:
            team_member_orm = TeamMemberORM.objects.get(user_id=user_id, team_id=team_id)
            return ModelParser.team_parser().parse_team_member(team_member_orm=team_member_orm)
        except TeamMemberORM.DoesNotExist:
            return None

    # ------------------------ Create TeamMember resource --------------------- #

    # ------------------------ Update TeamMember resource --------------------- #
    def sharing_invitations_confirm(self, user: User, email: str = None) -> Optional[User]:
        user_orm = self._get_user_orm(user_id=user.user_id)
        if not user_orm:
            return
        if not email:
            email = user_orm.get_from_cystack_id().get("email")
        if not email:
            return user
        sharing_invitations = TeamMemberORM.objects.filter(
            email=email, team__key__isnull=False, status=PM_MEMBER_STATUS_INVITED, team__personal_share=True
        )
        sharing_invitations.update(email=None, token_invitation=None, user=user_orm)
        return user

    # ------------------------ Delete TeamMember resource --------------------- #

