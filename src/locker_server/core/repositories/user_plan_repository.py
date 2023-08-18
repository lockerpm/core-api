from typing import Union, Dict, Optional
from abc import ABC, abstractmethod

from locker_server.core.entities.enterprise.enterprise import Enterprise
from locker_server.core.entities.user.user import User
from locker_server.core.entities.user_plan.pm_user_plan import PMUserPlan
from locker_server.shared.constants.transactions import DURATION_MONTHLY


class UserPlanRepository(ABC):
    # ------------------------ List PMUserPlan resource ------------------- #

    # ------------------------ Get PMUserPlan resource --------------------- #
    @abstractmethod
    def get_user_plan(self, user_id: int) -> Optional[PMUserPlan]:
        pass

    @abstractmethod
    def get_default_enterprise(self, user_id: int, enterprise_name: str = None,
                               create_if_not_exist=False) -> Optional[Enterprise]:
        pass

    # ------------------------ Create PMUserPlan resource --------------------- #
    @abstractmethod
    def add_to_family_sharing(self, family_user_plan_id: int, user_id: int = None,
                              email: str = None) -> Optional[PMUserPlan]:
        pass

    # ------------------------ Update PMUserPlan resource --------------------- #
    @abstractmethod
    def update_plan(self, user_id: int, plan_type_alias: str, duration: str = DURATION_MONTHLY, scope: str = None,
                    **kwargs):
        pass

    @abstractmethod
    def set_personal_trial_applied(self, user_id: int, applied: bool = True, platform: str = None):
        pass

    @abstractmethod
    def set_enterprise_trial_applied(self, user_id: int, applied: bool = True, platform: str = None):
        pass

    @abstractmethod
    def upgrade_member_family_plan(self, user: User) -> Optional[User]:
        pass

    # ------------------------ Delete PMUserPlan resource --------------------- #

