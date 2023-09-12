from typing import Union, Dict, Optional
from abc import ABC, abstractmethod

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_plan_model
from locker_server.core.entities.user_plan.pm_plan import PMPlan
from locker_server.core.repositories.plan_repository import PlanRepository


PMPlanORM = get_plan_model()
ModelParser = get_model_parser()


class PlanORMRepository(PlanRepository):
    # ------------------------ List PMPlan resource ------------------- #

    # ------------------------ Get PMPlan resource --------------------- #
    def get_plan_by_alias(self, alias: str) -> Optional[PMPlan]:
        try:
            plan_orm = PMPlanORM.objects.get(alias=alias)
            return ModelParser.user_plan_parser().parse_plan(plan_orm=plan_orm)
        except PMPlanORM.DoesNotExist:
            return None

    # ------------------------ Create PMPlan resource --------------------- #

    # ------------------------ Update PMPlan resource --------------------- #

    # ------------------------ Delete PMPlan resource --------------------- #

