from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_user_model, get_enterprise_domain_model, \
    get_enterprise_member_model, get_enterprise_group_member_model, get_enterprise_model, get_event_model
from locker_server.core.entities.enterprise.enterprise import Enterprise
from locker_server.core.entities.user.user import User
from locker_server.core.repositories.enterprise_member_repository import EnterpriseMemberRepository
from locker_server.core.repositories.enterprise_repository import EnterpriseRepository
from locker_server.shared.constants.enterprise_members import E_MEMBER_ROLE_MEMBER, E_MEMBER_STATUS_CONFIRMED
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
EnterpriseORM = get_enterprise_model()
EventORM = get_event_model()
ModelParser = get_model_parser()


class EnterpriseORMRepository(EnterpriseRepository):
    @staticmethod
    def _get_user_orm(user_id: int) -> Optional[UserORM]:
        try:
            return UserORM.objects.get(id=user_id)
        except UserORM.DoesNotExist:
            return None

    @staticmethod
    def _get_enterprise_orm(enterprise_id: str) -> Optional[UserORM]:
        try:
            return EnterpriseORM.objects.get(id=enterprise_id)
        except EnterpriseORM.DoesNotExist:
            return None

    # ------------------------ List Enterprise resource ------------------- #
    def list_user_enterprises(self, user_id: int, **filter_params) -> List[Enterprise]:
        enterprises_orm = EnterpriseORM.objects.filter(
            enterprise_members__user_id=user_id
        ).order_by('-creation_date')
        status_param = filter_params.get("status")
        is_activated_param = filter_params.get("is_activated")
        if status_param:
            enterprises_orm = enterprises_orm.filter(enterprise_members__status=status_param)
        if is_activated_param:
            enterprises_orm = enterprises_orm.filter(enterprise_members__is_activated=is_activated_param)
        return [ModelParser.enterprise_parser().parse_enterprise(enterprise_orm=enterprise_orm)
                for enterprise_orm in enterprises_orm]

    # ------------------------ Get Enterprise resource --------------------- #

    # ------------------------ Create Enterprise resource --------------------- #

    # ------------------------ Update Enterprise resource --------------------- #

    # ------------------------ Delete Enterprise resource --------------------- #
    def delete_completely(self, enterprise: Enterprise):
        enterprise_id = enterprise.enterprise_id
        self.clear_data(enterprise=enterprise)
        try:
            EnterpriseORM.objects.get(id=enterprise_id).delete()
        except EnterpriseORM.DoesNotExist:
            pass
        # Delete all events
        EventORM.objects.filter(team_id=enterprise_id).delete()

    def clear_data(self, enterprise: Enterprise):
        enterprise_orm = self._get_enterprise_orm(enterprise_id=enterprise.enterprise_id)
        enterprise_orm.enterprise_members.order_by('id').delete()
        enterprise_orm.policies.order_by('id').delete()
        enterprise_orm.domains.all().order_by('id').delete()
        groups_orm = enterprise_orm.groups.order_by('id')
        for group_orm in groups_orm:
            group_orm.full_delete()
