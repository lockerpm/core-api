from typing import List

from locker_server.core.entities.enterprise.policy.policy import EnterprisePolicy
from locker_server.core.repositories.enterprise_member_repository import EnterpriseMemberRepository
from locker_server.core.repositories.enterprise_policy_repository import EnterprisePolicyRepository
from locker_server.core.repositories.enterprise_repository import EnterpriseRepository


class EnterpriseService:
    """
    This class represents Use Cases related User
    """

    def __init__(self, enterprise_repository: EnterpriseRepository,
                 enterprise_member_repository: EnterpriseMemberRepository,
                 enterprise_policy_repository: EnterprisePolicyRepository):
        self.enterprise_repository = enterprise_repository
        self.enterprise_member_repository = enterprise_member_repository
        self.enterprise_policy_repository = enterprise_policy_repository

    def list_policies_by_user(self, user_id: int) -> List[EnterprisePolicy]:
        return self.enterprise_policy_repository.list_policies_by_user(user_id=user_id)

    def is_in_enterprise(self, user_id: int, enterprise_locked: bool = None) -> bool:
        return self.enterprise_member_repository.is_in_enterprise(user_id=user_id, enterprise_locked=enterprise_locked)

