from typing import Union, Dict, Optional
from abc import ABC, abstractmethod

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_payment_model
from locker_server.core.entities.user.user import User
from locker_server.core.entities.user_plan.pm_user_plan import PMUserPlan
from locker_server.core.repositories.payment_repository import PaymentRepository
from locker_server.shared.constants.transactions import LIST_UTM_SOURCE_PROMOTIONS, PAYMENT_STATUS_PAID

PaymentORM = get_payment_model()
ModelParser = get_model_parser()


class PaymentORMRepository(PaymentRepository):
    # ------------------------ List PMUserPlan resource ------------------- #

    # ------------------------ Get PMUserPlan resource --------------------- #
    def is_blocked_by_source(self, user_id: int, utm_source: str) -> bool:
        if utm_source in LIST_UTM_SOURCE_PROMOTIONS and PaymentORM.objects.filter(
            user_id=user_id, status=PAYMENT_STATUS_PAID
        ).exists() is False:
            return True
        return False

    # ------------------------ Create PMUserPlan resource --------------------- #

    # ------------------------ Update PMUserPlan resource --------------------- #

    # ------------------------ Delete PMUserPlan resource --------------------- #

