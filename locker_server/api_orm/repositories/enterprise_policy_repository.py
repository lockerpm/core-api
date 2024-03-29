from typing import Union, Dict, Optional, List

from django.db.models import ExpressionWrapper, F, FloatField

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models import PolicyPasswordORM, PolicyMasterPasswordORM, PolicyFailedLoginORM, \
    PolicyPasswordlessORM, Policy2FAORM
from locker_server.api_orm.models.wrapper import get_user_model, get_enterprise_domain_model, \
    get_enterprise_member_model, get_enterprise_group_member_model, get_enterprise_model, get_enterprise_policy_model
from locker_server.core.entities.enterprise.policy.policy import EnterprisePolicy
from locker_server.core.entities.enterprise.policy.policy_2fa import Policy2FA
from locker_server.core.entities.enterprise.policy.policy_failed_login import PolicyFailedLogin
from locker_server.core.entities.enterprise.policy.policy_master_password import PolicyMasterPassword
from locker_server.core.entities.enterprise.policy.policy_password import PolicyPassword
from locker_server.core.entities.enterprise.policy.policy_passwordless import PolicyPasswordless
from locker_server.core.repositories.enterprise_policy_repository import EnterprisePolicyRepository
from locker_server.shared.constants.enterprise_members import E_MEMBER_STATUS_CONFIRMED
from locker_server.shared.constants.policy import *

UserORM = get_user_model()
DomainORM = get_enterprise_domain_model()
EnterpriseMemberORM = get_enterprise_member_model()
EnterpriseGroupMemberORM = get_enterprise_group_member_model()
EnterpriseORM = get_enterprise_model()
EnterprisePolicyORM = get_enterprise_policy_model()
ModelParser = get_model_parser()


class EnterprisePolicyORMRepository(EnterprisePolicyRepository):
    def create_detail(self, policy: EnterprisePolicyORM, policy_type: str, **kwargs):
        if policy_type == POLICY_TYPE_PASSWORD_REQUIREMENT:
            PolicyPasswordORM.create(policy, **kwargs)
        elif policy_type == POLICY_TYPE_MASTER_PASSWORD_REQUIREMENT:
            PolicyMasterPasswordORM.create(policy, **kwargs)
        elif policy_type == POLICY_TYPE_BLOCK_FAILED_LOGIN:
            PolicyFailedLoginORM.create(policy, **kwargs)
        elif policy_type == POLICY_TYPE_PASSWORDLESS:
            PolicyPasswordlessORM.create(policy, **kwargs)
        elif policy_type == POLICY_TYPE_2FA:
            Policy2FAORM.create(policy, **kwargs)

    def get_policy_config(self, policy_type: str, policy_id: str):
        if policy_type == POLICY_TYPE_PASSWORD_REQUIREMENT:
            config = self.get_policy_password_requirement(
                policy_id=policy_id
            )
        elif policy_type == POLICY_TYPE_MASTER_PASSWORD_REQUIREMENT:
            config = self.get_policy_master_password_requirement(
                policy_id=policy_id,
            )
        elif policy_type == POLICY_TYPE_BLOCK_FAILED_LOGIN:
            config = self.get_policy_block_failed_login(
                policy_id=policy_id,

            )
        elif policy_type == POLICY_TYPE_PASSWORDLESS:
            config = self.get_policy_type_passwordless(
                policy_id=policy_id,
            )
        elif policy_type == POLICY_TYPE_2FA:
            config = self.get_policy_2fa(
                policy_id=policy_id,
            )
        else:
            config = None
        if config:
            return config.get_config_json()
        return config

    # ------------------------ List EnterprisePolicy resource ------------------- #
    def list_policies_by_user(self, user_id: int) -> List[EnterprisePolicy]:
        enterprise_ids = list(EnterpriseMemberORM.objects.filter(
            user_id=user_id, status=E_MEMBER_STATUS_CONFIRMED
        ).values_list('enterprise_id', flat=True))
        policies_orm = EnterprisePolicyORM.objects.filter(enterprise_id__in=enterprise_ids).select_related('enterprise')
        user_enterprise_polices = [
            ModelParser.enterprise_parser().parse_enterprise_policy(enterprise_policy_orm=policy_orm)
            for policy_orm in policies_orm
        ]
        for policy in user_enterprise_polices:
            policy_id = policy.policy_id
            config = self.get_policy_config(policy_type=policy.policy_type, policy_id=policy_id)
            policy.config = config

        return user_enterprise_polices

    def list_2fa_policy(self, enterprise_ids: List[str], enabled: bool = True) -> List[Policy2FA]:
        policies_orm = EnterprisePolicyORM.objects.filter(
            enterprise_id__in=enterprise_ids, policy_type=POLICY_TYPE_2FA, enabled=enabled
        ).select_related('enterprise')
        return [ModelParser.enterprise_parser().parse_policy_2fa(policy_2fa_orm=policy_2fa_orm)
                for policy_2fa_orm in policies_orm]

    def list_enterprise_policies(self, enterprise_id: str) -> List[EnterprisePolicy]:
        policies_orm = EnterprisePolicyORM.objects.filter(
            enterprise_id=enterprise_id
        ).order_by("id").select_related('enterprise')
        return [
            ModelParser.enterprise_parser().parse_enterprise_policy(
                enterprise_policy_orm=policy_orm
            )
            for policy_orm in policies_orm
        ]

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
        policy_2fa_orm = Policy2FAORM.objects.filter(
            policy__enterprise_id=enterprise_id, policy__policy_type=POLICY_TYPE_2FA, policy__enabled=True
        ).first()
        return ModelParser.enterprise_parser().parse_policy_2fa(policy_2fa_orm=policy_2fa_orm) \
            if policy_2fa_orm else None

    def get_policy_by_type(self, enterprise_id: str, policy_type: str) -> Optional[EnterprisePolicy]:
        try:
            policy_orm = EnterprisePolicyORM.objects.get(
                enterprise_id=enterprise_id,
                policy_type=policy_type
            )
        except EnterprisePolicyORM.DoesNotExist:
            return None
        return ModelParser.enterprise_parser().parse_enterprise_policy(enterprise_policy_orm=policy_orm)

    def get_policy_password_requirement(self, policy_id: str) -> Optional[PolicyPassword]:
        try:
            policy_password_orm = PolicyPasswordORM.objects.get(
                policy_id=policy_id
            )

        except PolicyPasswordORM.DoesNotExist:
            return None
        return ModelParser.enterprise_parser().parse_policy_password(
            policy_password_orm=policy_password_orm
        )

    def get_policy_master_password_requirement(self, policy_id: str) -> Optional[PolicyMasterPassword]:
        try:
            policy_master_password_orm = PolicyMasterPasswordORM.objects.get(
                policy_id=policy_id
            )
        except PolicyMasterPasswordORM.DoesNotExist:
            return None
        return ModelParser.enterprise_parser().parse_policy_master_password(
            policy_master_password_orm=policy_master_password_orm
        )

    def get_policy_block_failed_login(self, policy_id: str) -> Optional[PolicyFailedLogin]:
        try:
            policy_failed_login_orm = PolicyFailedLoginORM.objects.get(
                policy_id=policy_id
            )
        except PolicyFailedLoginORM.DoesNotExist:
            return None

        return ModelParser.enterprise_parser().parse_policy_failed_login(
            policy_failed_login_orm=policy_failed_login_orm
        )

    def get_policy_type_passwordless(self, policy_id: str) -> Optional[PolicyPasswordless]:
        try:
            policy_passwordless_orm = PolicyPasswordlessORM.objects.get(
                policy_id=policy_id
            )
        except PolicyPasswordlessORM.DoesNotExist:
            return None

        return ModelParser.enterprise_parser().parse_policy_passwordless(
            policy_passwordless_orm=policy_passwordless_orm
        )

    def get_policy_2fa(self, policy_id: str) -> Optional[Policy2FA]:
        try:
            policy_2fa_orm = Policy2FAORM.objects.get(
                policy_id=policy_id
            )
        except Policy2FAORM.DoesNotExist:
            return None
        return ModelParser.enterprise_parser().parse_policy_2fa(
            policy_2fa_orm=policy_2fa_orm
        )

    # ------------------------ Create EnterprisePolicy resource --------------------- #

    def create_policy(self, policy_create_data) -> EnterprisePolicy:
        enterprise_id = policy_create_data.get('enterprise_id')
        policy_type = policy_create_data.get('policy_type')
        new_policy_orm, is_created = EnterprisePolicyORM.objects.get_or_create(
            enterprise_id=enterprise_id,
            policy_type=policy_type,
            defaults={
                "enterprise_id": enterprise_id, "policy_type": policy_type
            }

        )
        self.create_detail(new_policy_orm, **policy_create_data)
        return ModelParser.enterprise_parser().parse_enterprise_policy(enterprise_policy_orm=new_policy_orm)

    # ------------------------ Update EnterprisePolicy resource --------------------- #
    def update_policy_password_requirement(self, policy_id: str, update_data) -> Optional[PolicyPassword]:
        try:
            policy_password_orm = PolicyPasswordORM.objects.get(
                policy_id=policy_id
            )

        except PolicyPasswordORM.DoesNotExist:
            return None
        policy_password_orm.min_length = update_data.get("min_length", policy_password_orm.min_length)
        policy_password_orm.require_lower_case = update_data.get(
            "require_lower_case",
            policy_password_orm.require_lower_case
        )
        policy_password_orm.require_upper_case = update_data.get(
            "require_upper_case",
            policy_password_orm.require_upper_case
        )
        policy_password_orm.require_special_character = update_data.get(
            "require_special_character",
            policy_password_orm.require_special_character
        )
        policy_password_orm.require_digit = update_data.get(
            "require_digit", policy_password_orm.require_digit
        )
        policy_password_orm.save()
        policy_password_orm.policy.enabled = update_data.get("enabled", policy_password_orm.policy.enabled)
        policy_password_orm.policy.save()
        return ModelParser.enterprise_parser().parse_policy_password(
            policy_password_orm=policy_password_orm
        )

    def update_policy_master_password_requirement(self, policy_id: str, update_data) -> Optional[PolicyMasterPassword]:
        try:
            policy_master_password_orm = PolicyMasterPasswordORM.objects.get(
                policy_id=policy_id
            )
        except PolicyMasterPasswordORM.DoesNotExist:
            return None
        policy_master_password_orm.min_length = update_data.get("min_length", policy_master_password_orm.min_length)
        policy_master_password_orm.require_lower_case = update_data.get(
            "require_lower_case",
            policy_master_password_orm.require_lower_case
        )
        policy_master_password_orm.require_upper_case = update_data.get(
            "require_upper_case",
            policy_master_password_orm.require_upper_case
        )
        policy_master_password_orm.require_special_character = update_data.get(
            "require_special_character",
            policy_master_password_orm.require_special_character
        )
        policy_master_password_orm.require_digit = update_data.get(
            "require_digit", policy_master_password_orm.require_digit
        )
        policy_master_password_orm.save()
        policy_master_password_orm.policy.enabled = update_data.get("enabled",
                                                                    policy_master_password_orm.policy.enabled)
        policy_master_password_orm.policy.save()
        return ModelParser.enterprise_parser().parse_policy_master_password(
            policy_master_password_orm=policy_master_password_orm
        )

    def update_policy_block_failed_login(self, policy_id: str, update_data) -> Optional[PolicyFailedLogin]:
        try:
            policy_failed_login_orm = PolicyFailedLoginORM.objects.get(
                policy_id=policy_id
            )
        except PolicyFailedLoginORM.DoesNotExist:
            return None
        policy_failed_login_orm.failed_login_attempts = update_data.get(
            "failed_login_attempts",
            policy_failed_login_orm.failed_login_attempts
        )
        policy_failed_login_orm.failed_login_duration = update_data.get(
            "failed_login_duration",
            policy_failed_login_orm.failed_login_duration
        )
        policy_failed_login_orm.failed_login_block_time = update_data.get(
            "failed_login_block_time",
            policy_failed_login_orm.failed_login_block_time
        )
        policy_failed_login_orm.failed_login_owner_email = update_data.get(
            "failed_login_owner_email",
            policy_failed_login_orm.failed_login_owner_email
        )
        policy_failed_login_orm.save()
        policy_failed_login_orm.policy.enabled = update_data.get(
            "enabled", policy_failed_login_orm.policy.enabled
        )
        policy_failed_login_orm.policy.save()
        return ModelParser.enterprise_parser().parse_policy_failed_login(
            policy_failed_login_orm=policy_failed_login_orm
        )

    def update_policy_type_passwordless(self, policy_id: str, update_data) -> Optional[PolicyPasswordless]:
        try:
            policy_passwordless_orm = PolicyPasswordlessORM.objects.get(
                policy_id=policy_id
            )
        except PolicyPasswordlessORM.DoesNotExist:
            return None
        policy_passwordless_orm.only_allow_passwordless = update_data.get(
            "only_allow_passwordless",
            policy_passwordless_orm.only_allow_passwordless
        )
        policy_passwordless_orm.save()
        policy_passwordless_orm.policy.enabled = update_data.get(
            "enabled", policy_passwordless_orm.policy.enabled
        )
        policy_passwordless_orm.policy.save()
        return ModelParser.enterprise_parser().parse_policy_passwordless(
            policy_passwordless_orm=policy_passwordless_orm
        )

    def update_policy_2fa(self, policy_id: str, update_data) -> Optional[Policy2FA]:
        try:
            policy_2fa_orm = Policy2FAORM.objects.get(
                policy_id=policy_id
            )
        except Policy2FAORM.DoesNotExist:
            return None
        policy_2fa_orm.only_admin = update_data.get("only_admin", policy_2fa_orm.only_admin)
        policy_2fa_orm.save()
        policy_2fa_orm.policy.enabled = update_data.get("enabled", policy_2fa_orm.policy.enabled)
        policy_2fa_orm.policy.save()
        return ModelParser.enterprise_parser().parse_policy_2fa(
            policy_2fa_orm=policy_2fa_orm
        )
    # ------------------------ Delete EnterprisePolicy resource --------------------- #
