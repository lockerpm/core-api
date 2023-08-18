from typing import Union, Dict, Optional
from abc import ABC, abstractmethod

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_user_model, get_team_member_model
from locker_server.core.entities.user.user import User
from locker_server.core.repositories.team_member_repository import TeamMemberRepository
from locker_server.shared.constants.members import PM_MEMBER_STATUS_INVITED

UserORM = get_user_model()
TeamMemberORM = get_team_member_model()
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

    # ------------------------ Get TeamMember resource --------------------- #

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

