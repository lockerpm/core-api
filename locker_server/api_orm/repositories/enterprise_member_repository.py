from typing import Union, Dict, Optional
from abc import ABC, abstractmethod

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_user_model, get_enterprise_domain_model, \
    get_enterprise_member_model, get_enterprise_group_member_model
from locker_server.core.entities.enterprise.member.enterprise_member import EnterpriseMember
from locker_server.core.entities.user.user import User
from locker_server.core.repositories.enterprise_member_repository import EnterpriseMemberRepository
from locker_server.shared.constants.enterprise_members import E_MEMBER_ROLE_MEMBER, E_MEMBER_STATUS_REQUESTED, \
    E_MEMBER_STATUS_INVITED, E_MEMBER_STATUS_CONFIRMED
from locker_server.shared.constants.members import PM_MEMBER_STATUS_INVITED
from locker_server.shared.log.cylog import CyLog
from locker_server.shared.utils.network import extract_root_domain

UserORM = get_user_model()
DomainORM = get_enterprise_domain_model()
EnterpriseMemberORM = get_enterprise_member_model()
EnterpriseGroupMemberORM = get_enterprise_group_member_model()
# PMPlanORM = get_plan_model()
# PMUserPlanORM = get_user_plan_model()
# EnterpriseMemberRoleORM = get_enterprise_member_role_model()
# EnterpriseMemberORM = get_enterprise_member_model()
# EnterpriseORM = get_enterprise_model()
ModelParser = get_model_parser()


class EnterpriseMemberORMRepository(EnterpriseMemberRepository):
    @staticmethod
    def _get_user_orm(user_id: int) -> Optional[UserORM]:
        try:
            return UserORM.objects.get(id=user_id)
        except UserORM.DoesNotExist:
            return None

    # ------------------------ List EnterpriseMember resource ------------------- #

    # ------------------------ Get EnterpriseMember resource --------------------- #
    def get_primary_member(self, enterprise_id: str) -> Optional[EnterpriseMember]:
        try:
            enterprise_member_orm = EnterpriseMemberORM.objects.get(
                enterprise_id=enterprise_id, is_primary=True
            )
        except EnterpriseMemberORM.DoesNotExist:
            return None
        return ModelParser.enterprise_parser().parse_enterprise_member(enterprise_member_orm=enterprise_member_orm)

    def get_enterprise_member_by_user_id(self, enterprise_id: str, user_id: int) -> Optional[EnterpriseMember]:
        try:
            enterprise_member_orm = EnterpriseMemberORM.objects.get(
                enterprise_id=enterprise_id, user_id=user_id
            )
            return ModelParser.enterprise_parser().parse_enterprise_member(enterprise_member_orm=enterprise_member_orm)
        except EnterpriseMemberORM.DoesNotExist:
            return None

    def lock_login_account_belong_enterprise(self, user_id: int) -> bool:
        return EnterpriseMemberORM.objects.filter(
            user_id=user_id, status__in=[E_MEMBER_STATUS_REQUESTED, E_MEMBER_STATUS_INVITED], domain__isnull=False
        ).exists()

    def is_active_enterprise_member(self, user_id: int) -> bool:
        return EnterpriseMemberORM.objects.filter(
            user_id=user_id, status=E_MEMBER_STATUS_CONFIRMED, is_activated=True, enterprise__locked=False
        )

    def is_in_enterprise(self, user_id: int, enterprise_locked: bool = None) -> bool:
        if enterprise_locked is not None:
            return EnterpriseMemberORM.objects.filter(user_id=user_id, enterprise__locked=enterprise_locked).exists()
        return EnterpriseMemberORM.objects.filter(user_id=user_id).exists()

    # ------------------------ Create EnterpriseMember resource --------------------- #

    # ------------------------ Update EnterpriseMember resource --------------------- #
    def enterprise_invitations_confirm(self, user: User, email: str = None) -> Optional[User]:
        user_orm = self._get_user_orm(user_id=user.user_id)
        if not user_orm:
            return
        if not email:
            email = user_orm.get_from_cystack_id().get("email")
        if not email:
            return user
        # Add this user into the Enterprise if the mail domain belongs to an Enterprise
        belong_enterprise_domain = False
        try:
            email_domain = email.split("@")[1]
            root_domain = extract_root_domain(domain=email_domain)
            domain_orm = DomainORM.objects.filter(root_domain=root_domain, verification=True).first()
            if domain_orm:
                belong_enterprise_domain = True
                EnterpriseMemberORM.retrieve_or_create_by_user(
                    enterprise=domain_orm.enterprise, user=user_orm, role_id=E_MEMBER_ROLE_MEMBER,
                    **{"domain": domain_orm}
                )
                # Cancel all other invitations
                EnterpriseMemberORM.objects.filter(email=email, status=PM_MEMBER_STATUS_INVITED).delete()
        except (ValueError, IndexError, AttributeError):
            CyLog.warning(**{"message": f"[enterprise_invitations_confirm] Can not get email: {user_orm} {email}"})
            pass
        # Update existed invitations
        if belong_enterprise_domain is False:
            enterprise_invitations = EnterpriseMemberORM.objects.filter(email=email, status=PM_MEMBER_STATUS_INVITED)
            enterprise_invitations.update(email=None, token_invitation=None, user=user_orm)
        return user

    def enterprise_share_groups_confirm(self, user: User) -> Optional[User]:
        from locker_server.shared.external_services.locker_background.constants import BG_ENTERPRISE_GROUP
        from locker_server.shared.external_services.locker_background.background_factory import BackgroundFactory

        enterprise_group_ids = EnterpriseGroupMemberORM.objects.filter(
            member__user_id=user.user_id
        ).values_list('group_id', flat=True)
        BackgroundFactory.get_background(bg_name=BG_ENTERPRISE_GROUP).run(
            func_name="add_group_member_to_share", **{
                "enterprise_group_ids": list(enterprise_group_ids),
                "new_member_ids": [user.user_id]
            }
        )

        # for enterprise_group_member_orm in enterprise_group_members_orm:
        #     BackgroundFactory.get_background(bg_name=BG_ENTERPRISE_GROUP).run(
        #         func_name="add_group_member_to_share", **{
        #             "enterprise_group": enterprise_group_member.group,
        #             "new_member_ids": [user.user_id]
        #         }
        #     )
        return user

    # ------------------------ Delete EnterpriseMember resource --------------------- #

