from typing import Union, Dict, Optional
from abc import ABC, abstractmethod

from locker_server.core.entities.user_plan.pm_plan import PMPlan


class PlanRepository(ABC):
    # ------------------------ List PMPlan resource ------------------- #

    # ------------------------ Get PMPlan resource --------------------- #
    @abstractmethod
    def get_plan_by_alias(self, alias: str) -> Optional[PMPlan]:
        pass

    # ------------------------ Create PMPlan resource --------------------- #

    # ------------------------ Update PMPlan resource --------------------- #

    # ------------------------ Delete PMPlan resource --------------------- #

