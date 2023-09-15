from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from django.db.models import ExpressionWrapper, F, FloatField

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_user_model, get_enterprise_domain_model, \
    get_enterprise_member_model, get_enterprise_group_member_model, get_enterprise_model, get_enterprise_policy_model
from locker_server.core.entities.enterprise.enterprise import Enterprise
from locker_server.core.entities.enterprise.policy.policy import EnterprisePolicy
from locker_server.core.entities.enterprise.policy.policy_2fa import Policy2FA
from locker_server.core.entities.enterprise.policy.policy_failed_login import PolicyFailedLogin
from locker_server.core.entities.event.event import Event
from locker_server.core.entities.user.user import User
from locker_server.core.repositories.enterprise_policy_repository import EnterprisePolicyRepository
from locker_server.shared.constants.enterprise_members import E_MEMBER_STATUS_CONFIRMED
from locker_server.shared.constants.policy import POLICY_TYPE_BLOCK_FAILED_LOGIN, POLICY_TYPE_2FA

UserORM = get_user_model()
DomainORM = get_enterprise_domain_model()
EnterpriseMemberORM = get_enterprise_member_model()
EnterpriseGroupMemberORM = get_enterprise_group_member_model()
# PMPlanORM = get_plan_model()
# PMUserPlanORM = get_user_plan_model()
# EnterpriseMemberRoleORM = get_enterprise_member_role_model()
# EnterpriseMemberORM = get_enterprise_member_model()
EnterpriseORM = get_enterprise_model()
EnterprisePolicyORM = get_enterprise_policy_model()
ModelParser = get_model_parser()


class EnterprisePolicyORMRepository(EnterprisePolicyRepository):
    # ------------------------ List EnterprisePolicy resource ------------------- #
    def list_policies_by_user(self, user_id: int) -> List[EnterprisePolicy]:
        enterprise_ids = list(EnterpriseMemberORM.objects.filter(
            user_id=user_id, status=E_MEMBER_STATUS_CONFIRMED
        ).values_list('enterprise_id', flat=True))
        policies_orm = EnterprisePolicyORM.objects.filter(enterprise_id__in=enterprise_ids).select_related('enterprise')
        return [
            ModelParser.enterprise_parser().parse_enterprise_policy(enterprise_policy_orm=policy_orm)
            for policy_orm in policies_orm
        ]

    def list_2fa_policy(self, enterprise_ids: List[str], enabled: bool = True) -> List[Policy2FA]:
        policies_orm = EnterprisePolicyORM.objects.filter(
            enterprise_id__in=enterprise_ids, policy_type=POLICY_TYPE_2FA, enabled=enabled
        )
        return [ModelParser.enterprise_parser().parse_policy_2fa(policy_2fa_orm=policy_2fa_orm)
                for policy_2fa_orm in policies_orm]

    # ------------------------ Get EnterprisePolicy resource --------------------- #
    def get_block_failed_login_policy(self, user_id: int) -> Optional[PolicyFailedLogin]:
        enterprise_ids = list(EnterpriseMemberORM.objects.filter(
            user_id=user_id, status=E_MEMBER_STATUS_CONFIRMED
        ).values_list('enterprise_id', flat=True))
        policy_orm = EnterprisePolicyORM.objects.filter(
            enterprise_id__in=enterprise_ids,
            policy_type=POLICY_TYPE_BLOCK_FAILED_LOGIN,
            enabled=True
        ).annotate(
            rate_limit=ExpressionWrapper(
                F('policy_failed_login__failed_login_attempts') * 1.0 /
                F('policy_failed_login__failed_login_duration'), output_field=FloatField()
            )
        ).order_by('rate_limit').first()
        if not policy_orm:
            return None
        return ModelParser.enterprise_parser().parse_policy_failed_login(policy_orm.policy_failed_login)

    def get_enterprise_2fa_policy(self, enterprise_id: str) -> Optional[Policy2FA]:
        policy_2fa_orm = EnterprisePolicyORM.objects.filter(
            enterprise_id=enterprise_id, policy_type=POLICY_TYPE_2FA, enabled=True
        ).first()
        return ModelParser.enterprise_parser().parse_policy_2fa(policy_2fa_orm=policy_2fa_orm) \
            if policy_2fa_orm else None

    # ------------------------ Create EnterprisePolicy resource --------------------- #

    # ------------------------ Update EnterprisePolicy resource --------------------- #

    # ------------------------ Delete EnterprisePolicy resource --------------------- #
