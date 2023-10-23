from typing import List, Optional, NoReturn

from locker_server.core.entities.enterprise.domain.domain import Domain
from locker_server.core.entities.enterprise.enterprise import Enterprise
from locker_server.core.entities.enterprise.member.enterprise_member import EnterpriseMember
from locker_server.core.entities.enterprise.payment.billing_contact import EnterpriseBillingContact
from locker_server.core.entities.enterprise.policy.policy import EnterprisePolicy
from locker_server.core.entities.user.user import User
from locker_server.core.exceptions.country_exception import CountryDoesNotExistException
from locker_server.core.exceptions.enterprise_billing_contact_exception import \
    EnterpriseBillingContactDoesNotExistException
from locker_server.core.exceptions.enterprise_domain_exception import *
from locker_server.core.exceptions.enterprise_exception import EnterpriseDoesNotExistException
from locker_server.core.exceptions.enterprise_member_exception import EnterpriseMemberPrimaryDoesNotExistException
from locker_server.core.exceptions.enterprise_policy_exception import EnterprisePolicyDoesNotExistException
from locker_server.core.repositories.country_repository import CountryRepository
from locker_server.core.repositories.enterprise_billing_contact_repository import EnterpriseBillingContactRepository
from locker_server.core.repositories.enterprise_domain_repository import EnterpriseDomainRepository
from locker_server.core.repositories.enterprise_member_repository import EnterpriseMemberRepository
from locker_server.core.repositories.enterprise_policy_repository import EnterprisePolicyRepository
from locker_server.core.repositories.enterprise_repository import EnterpriseRepository
from locker_server.shared.constants.enterprise_members import E_MEMBER_ROLE_PRIMARY_ADMIN, E_MEMBER_STATUS_CONFIRMED
from locker_server.shared.constants.policy import LIST_POLICY_TYPE, POLICY_TYPE_PASSWORD_REQUIREMENT, \
    POLICY_TYPE_MASTER_PASSWORD_REQUIREMENT, POLICY_TYPE_BLOCK_FAILED_LOGIN, POLICY_TYPE_PASSWORDLESS, POLICY_TYPE_2FA


class EnterpriseService:
    """
    This class represents Use Cases related User
    """

    def __init__(self, enterprise_repository: EnterpriseRepository,
                 enterprise_member_repository: EnterpriseMemberRepository,
                 enterprise_policy_repository: EnterprisePolicyRepository,
                 enterprise_billing_contact_repository: EnterpriseBillingContactRepository,
                 enterprise_domain_repository: EnterpriseDomainRepository,
                 country_repository: CountryRepository
                 ):
        self.enterprise_repository = enterprise_repository
        self.enterprise_member_repository = enterprise_member_repository
        self.enterprise_policy_repository = enterprise_policy_repository
        self.enterprise_billing_contact_repository = enterprise_billing_contact_repository
        self.enterprise_domain_repository = enterprise_domain_repository
        self.country_repository = country_repository

    def list_policies_by_user(self, user_id: int) -> List[EnterprisePolicy]:
        return self.enterprise_policy_repository.list_policies_by_user(user_id=user_id)

    def get_enterprise_by_id(self, enterprise_id: str) -> Optional[Enterprise]:
        enterprise = self.enterprise_repository.get_enterprise_by_id(
            enterprise_id=enterprise_id
        )
        if not enterprise:
            raise EnterpriseDoesNotExistException
        return enterprise

    def get_primary_member(self, enterprise_id: str) -> Optional[EnterpriseMember]:
        primary_member = self.enterprise_member_repository.get_primary_member(
            enterprise_id=enterprise_id
        )
        if not primary_member:
            raise EnterpriseMemberPrimaryDoesNotExistException
        return primary_member

    def create_default_enterprise_policies(self, enterprise_id: str) -> List[EnterprisePolicy]:
        policies = []
        for policy_type in LIST_POLICY_TYPE:
            new_policy = self.enterprise_policy_repository.create_policy(
                policy_create_data={
                    "enterprise_id": enterprise_id,
                    "policy_type": policy_type
                }
            )
            policies.append(new_policy)
        return policies

    def list_enterprise_policies(self, enterprise_id: str) -> List[EnterprisePolicy]:
        enterprise = self.enterprise_repository.get_enterprise_by_id(enterprise_id)
        if not enterprise:
            raise EnterpriseDoesNotExistException
        policies = self.enterprise_policy_repository.list_enterprise_policies(
            enterprise_id=enterprise_id
        )
        if len(policies) < len(LIST_POLICY_TYPE):
            policies = self.create_default_enterprise_policies(enterprise_id=enterprise_id)
        for policy in policies:
            policy.config = self.get_policy_config(
                policy_id=policy.policy_id,
                policy_type=policy.policy_type
            )
        return policies

    def get_policy_by_type(self, enterprise_id: str, policy_type: str) -> Optional[EnterprisePolicy]:
        policy = self.enterprise_policy_repository.get_policy_by_type(
            enterprise_id=enterprise_id,
            policy_type=policy_type
        )
        policy.config = self.get_policy_config(
            policy_id=policy.policy_id,
            policy_type=policy.policy_type
        )
        if not policy:
            raise EnterprisePolicyDoesNotExistException
        return policy

    def update_policy(self, policy: EnterprisePolicy, policy_update_data) -> NoReturn:
        policy_type = policy.policy_type
        if policy_type == POLICY_TYPE_PASSWORD_REQUIREMENT:
            self.enterprise_policy_repository.update_policy_password_requirement(
                policy_id=policy.policy_id,
                update_data=policy_update_data
            )
        elif policy_type == POLICY_TYPE_MASTER_PASSWORD_REQUIREMENT:
            self.enterprise_policy_repository.update_policy_master_password_requirement(
                policy_id=policy.policy_id,
                update_data=policy_update_data
            )
        elif policy_type == POLICY_TYPE_BLOCK_FAILED_LOGIN:
            self.enterprise_policy_repository.update_policy_block_failed_login(
                policy_id=policy.policy_id,
                update_data=policy_update_data
            )
        elif policy_type == POLICY_TYPE_PASSWORDLESS:
            self.enterprise_policy_repository.update_policy_type_passwordless(
                policy_id=policy.policy_id,
                update_data=policy_update_data
            )
        elif policy_type == POLICY_TYPE_2FA:
            self.enterprise_policy_repository.update_policy_2fa(
                policy_id=policy.policy_id,
                update_data=policy_update_data
            )

    def get_policy_config(self, policy_id: str, policy_type: str):
        if policy_type == POLICY_TYPE_PASSWORD_REQUIREMENT:
            config = self.enterprise_policy_repository.get_policy_password_requirement(
                policy_id=policy_id
            )
        elif policy_type == POLICY_TYPE_MASTER_PASSWORD_REQUIREMENT:
            config = self.enterprise_policy_repository.get_policy_master_password_requirement(
                policy_id=policy_id,
            )
        elif policy_type == POLICY_TYPE_BLOCK_FAILED_LOGIN:
            config = self.enterprise_policy_repository.get_policy_block_failed_login(
                policy_id=policy_id,

            )
        elif policy_type == POLICY_TYPE_PASSWORDLESS:
            config = self.enterprise_policy_repository.get_policy_type_passwordless(
                policy_id=policy_id,
            )
        elif policy_type == POLICY_TYPE_2FA:
            config = self.enterprise_policy_repository.get_policy_2fa(
                policy_id=policy_id,
            )
        else:
            config = None
        return config

    def list_user_enterprises(self, user_id: int, **filters) -> List[Enterprise]:
        return self.enterprise_repository.list_user_enterprises(
            user_id=user_id,
            **filters
        )

    def list_enterprises(self, **filters) -> List[Enterprise]:
        return self.enterprise_repository.list_enterprises(**filters)

    def update_enterprise(self, enterprise_id: str, enterprise_update_data) -> Optional[Enterprise]:
        enterprise_country = enterprise_update_data.get("enterprise_country")
        if enterprise_country:
            country = self.country_repository.get_country_by_code(
                country_code=enterprise_country
            )
            if not country:
                raise CountryDoesNotExistException
        updated_enterprise = self.enterprise_repository.update_enterprise(
            enterprise_id=enterprise_id,
            enterprise_update_data=enterprise_update_data
        )
        if not updated_enterprise:
            raise EnterpriseDoesNotExistException
        return updated_enterprise

    def delete_enterprise_complete(self, enterprise: Enterprise):
        self.enterprise_repository.delete_completely(
            enterprise=enterprise
        )

    def count_unverified_domain(self, enterprise_id: str) -> int:
        return self.enterprise_domain_repository.count_unverified_domain(
            enterprise_id=enterprise_id
        )

    def is_in_enterprise(self, user_id: int, enterprise_locked: bool = None) -> bool:
        return self.enterprise_member_repository.is_in_enterprise(user_id=user_id, enterprise_locked=enterprise_locked)

    def create_enterprise(self, user: User, enterprise_create_data) -> Enterprise:
        enterprise_country = enterprise_create_data.get("enterprise_country")
        if enterprise_country:
            country = self.country_repository.get_country_by_code(
                country_code=enterprise_country
            )
            if not country:
                raise CountryDoesNotExistException
        enterprise_create_data.update({
            "members": [{
                "user_id": user.user_id,
                "role_id": E_MEMBER_ROLE_PRIMARY_ADMIN,
                "status": E_MEMBER_STATUS_CONFIRMED,
                "is_primary": True
            }]
        })
        return self.enterprise_repository.create_enterprise(
            enterprise_create_data=enterprise_create_data
        )
