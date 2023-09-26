from typing import Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.payment.payment import Payment
from locker_server.core.entities.payment.promo_code import PromoCode


class PaymentRepository(ABC):
    # ------------------------ List PMUserPlan resource ------------------- #
    @abstractmethod
    def list_all_invoices(self, **filter_params) -> List[Payment]:
        pass

    @abstractmethod
    def list_invoices_by_user(self, user_id: int, **filter_params) -> List[Payment]:
        pass

    # ------------------------ Get PMUserPlan resource --------------------- #
    @abstractmethod
    def is_blocked_by_source(self, user_id: int, utm_source: str) -> bool:
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int, payment_id: str) -> Optional[Payment]:
        pass

    @abstractmethod
    def get_by_payment_id(self, payment_id: str) -> Optional[Payment]:
        pass

    @abstractmethod
    def check_saas_promo_code(self, user_id: int, code: str) -> Optional[PromoCode]:
        pass

    @abstractmethod
    def check_promo_code(self, user_id: int, code: str, new_duration: str = None, new_plan: str = None) -> Optional[PromoCode]:
        pass

    # ------------------------ Create PMUserPlan resource --------------------- #
    @abstractmethod
    def create_education_promo_code(self, user_id: int) -> Optional[PromoCode]:
        pass

    # ------------------------ Update PMUserPlan resource --------------------- #
    @abstractmethod
    def update_promo_code_remaining_times(self, promo_code: PromoCode, amount: int = 1) -> PromoCode:
        pass

    # ------------------------ Delete PMUserPlan resource --------------------- #

