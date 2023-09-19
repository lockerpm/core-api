from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.enterprise.enterprise import Enterprise
from locker_server.core.entities.enterprise.policy.policy import EnterprisePolicy
from locker_server.core.entities.enterprise.policy.policy_2fa import Policy2FA
from locker_server.core.entities.enterprise.policy.policy_failed_login import PolicyFailedLogin
from locker_server.core.entities.event.event import Event
from locker_server.core.entities.user.user import User


class EnterprisePolicyRepository(ABC):
    # ------------------------ List EnterprisePolicy resource ------------------- #
    @abstractmethod
    def list_policies_by_user(self, user_id: int) -> List[EnterprisePolicy]:
        pass

    @abstractmethod
    def list_2fa_policy(self, enterprise_ids: List[str], enabled: bool = True) -> List[Policy2FA]:
        pass

    # ------------------------ Get EnterprisePolicy resource --------------------- #
    @abstractmethod
    def get_block_failed_login_policy(self, user_id: int) -> Optional[PolicyFailedLogin]:
        pass

    @abstractmethod
    def get_enterprise_2fa_policy(self, enterprise_id: str) -> Optional[Policy2FA]:
        pass

    # ------------------------ Create EnterprisePolicy resource --------------------- #

    # ------------------------ Update EnterprisePolicy resource --------------------- #

    # ------------------------ Delete EnterprisePolicy resource --------------------- #
