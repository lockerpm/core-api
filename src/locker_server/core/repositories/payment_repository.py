from typing import Union, Dict, Optional
from abc import ABC, abstractmethod

from locker_server.core.entities.user.user import User
from locker_server.core.entities.user_plan.pm_user_plan import PMUserPlan


class PaymentRepository(ABC):
    # ------------------------ List PMUserPlan resource ------------------- #

    # ------------------------ Get PMUserPlan resource --------------------- #
    @abstractmethod
    def is_blocked_by_source(self, user_id: int, utm_source: str) -> bool:
        pass

    # ------------------------ Create PMUserPlan resource --------------------- #

    # ------------------------ Update PMUserPlan resource --------------------- #

    # ------------------------ Delete PMUserPlan resource --------------------- #

