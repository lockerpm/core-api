import os
from typing import Optional, List
import stripe
import stripe.error

from django.db.models import F

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_payment_model, get_promo_code_model, get_user_model, \
    get_user_plan_model
from locker_server.core.entities.payment.payment import Payment
from locker_server.core.entities.payment.promo_code import PromoCode
from locker_server.core.repositories.payment_repository import PaymentRepository
from locker_server.shared.constants.transactions import LIST_UTM_SOURCE_PROMOTIONS, PAYMENT_STATUS_PAID, \
    PROMO_PERCENTAGE, DURATION_YEARLY, PLAN_TYPE_PM_PREMIUM, EDUCATION_PROMO_PREFIX
from locker_server.shared.utils.app import now, random_n_digit


PaymentORM = get_payment_model()
UserORM = get_user_model()
PromoCodeORM = get_promo_code_model()
PMUserPlanORM = get_user_plan_model()
ModelParser = get_model_parser()


class PaymentORMRepository(PaymentRepository):
    @staticmethod
    def _get_payment_orm(payment_id: str) -> Optional[PaymentORM]:
        try:
            return PaymentORM.objects.get(payment_id=payment_id)
        except PaymentORM.DoesNotExist:
            return None

    @staticmethod
    def _get_user_orm(user_id: int) -> Optional[UserORM]:
        try:
            return UserORM.objects.get(user_id=user_id)
        except UserORM.DoesNotExist:
            return None

    @staticmethod
    def _get_promo_code_orm(promo_code_id: str) -> Optional[PromoCodeORM]:
        try:
            return PromoCodeORM.objects.get(id=promo_code_id)
        except PromoCodeORM.DoesNotExist:
            return None

    @staticmethod
    def _get_current_plan_orm(user_id: int) -> PMUserPlanORM:
        user_orm = UserORM.objects.get(user_id=user_id)
        try:
            user_plan_orm = user_orm.pm_user_plan
        except (ValueError, AttributeError):
            user_plan_orm = PMUserPlanORM.update_or_create(user=user_orm)
        return user_plan_orm

    # ------------------------ List PMUserPlan resource ------------------- #
    def list_all_invoices(self, **filter_params) -> List[Payment]:
        payments_orm = PaymentORM.objects.filter().order_by('-created_time')
        from_param = filter_params.get("from")
        to_param = filter_params.get("to")
        status_param = filter_params.get("status")
        payment_method_param = filter_params.get("payment_method")
        user_id_param = filter_params.get("user_id")
        if from_param:
            payments_orm = payments_orm.filter(created_time__lte=from_param)
        if to_param:
            payments_orm = payments_orm.filter(created_time__gt=to_param)
        if status_param:
            payments_orm = payments_orm.filter(status=status_param)
        if payment_method_param:
            payments_orm = payments_orm.filter(payment_method=payment_method_param)
        if user_id_param:
            payments_orm = payments_orm.filter(user_id=user_id_param)
        payments_orm = payments_orm.select_related('user')
        payments = []
        for payment_orm in payments_orm:
            payments.append(ModelParser.payment_parser().parse_payment(payment_orm=payment_orm))
        return payments

    def list_invoices_by_user(self, user_id: int, **filter_params) -> List[Payment]:
        payments_orm = PaymentORM.objects.filter(user_id=user_id).order_by('-created_time')
        from_param = filter_params.get("from")
        to_param = filter_params.get("to")
        if from_param:
            payments_orm = payments_orm.filter(created_time__lte=from_param)
        if to_param:
            payments_orm = payments_orm.filter(created_time__gt=to_param)

        payments = []
        for payment_orm in payments_orm:
            payments.append(ModelParser.payment_parser().parse_payment(payment_orm=payment_orm))
        return payments

    # ------------------------ Get PMUserPlan resource --------------------- #
    def is_blocked_by_source(self, user_id: int, utm_source: str) -> bool:
        if utm_source in LIST_UTM_SOURCE_PROMOTIONS and PaymentORM.objects.filter(
            user_id=user_id, status=PAYMENT_STATUS_PAID
        ).exists() is False:
            return True
        return False

    def get_by_user_id(self, user_id: int, payment_id: str) -> Optional[Payment]:
        payment_orm = self._get_payment_orm(payment_id=payment_id)
        if not payment_orm or payment_orm.user_id != user_id:
            return None
        return ModelParser.payment_parser().parse_payment(payment_orm=payment_orm)

    def get_by_payment_id(self, payment_id: str) -> Optional[Payment]:
        payment_orm = self._get_payment_orm(payment_id=payment_id)
        if not payment_orm:
            return None
        return ModelParser.payment_parser().parse_payment(payment_orm=payment_orm)

    def check_saas_promo_code(self, user_id: int, code: str) -> Optional[PromoCode]:
        user_orm = self._get_user_orm(user_id=user_id)
        if not user_orm:
            return None
        promo_code_orm = PromoCodeORM.check_saas_valid(value=code, current_user=user_orm)
        if not promo_code_orm:
            return None
        return ModelParser.payment_parser().parse_promo_code(promo_code_orm=promo_code_orm)

    def check_promo_code(self, user_id: int, code: str, new_duration: str = None, new_plan: str = None) -> Optional[PromoCode]:
        user_orm = self._get_user_orm(user_id=user_id)
        if not user_orm:
            return None
        promo_code_orm = PromoCodeORM.check_valid(
            value=code, current_user=user_orm, new_duration=new_duration, new_plan=new_plan
        )
        if not promo_code_orm:
            return None
        return ModelParser.payment_parser().parse_promo_code(promo_code_orm=promo_code_orm)

    # ------------------------ Create PMUserPlan resource --------------------- #
    def create_education_promo_code(self, user_id: int) -> Optional[PromoCode]:
        # The promo code will be expired in one year
        expired_time = int(now() + 365 * 86400)
        value = 100
        code = f"{EDUCATION_PROMO_PREFIX}{random_n_digit(n=12)}".upper()
        only_user_id = user_id
        promo_code_data = {
            "type": PROMO_PERCENTAGE,
            "expired_time": expired_time,
            "code": code,
            "value": value,
            "duration": 1,
            "number_code": 1,
            "description_en": "Locker PromoCode Reward",
            "description_vi": "Locker PromoCode Reward",
            "only_user_id": only_user_id,
            "only_period": DURATION_YEARLY,
            "only_plan": PLAN_TYPE_PM_PREMIUM,
        }
        promo_code_orm = PromoCodeORM.create(**promo_code_data)

        # Create on Stripe
        if os.getenv("PROD_ENV") in ["prod", "staging"]:
            try:
                stripe.Coupon.create(
                    duration='once',
                    id="{}_yearly".format(promo_code_orm.id),
                    percent_off=value,
                    name=code,
                    redeem_by=expired_time
                )
            except stripe.error.StripeError:
                promo_code_orm.delete()
                return None
        return ModelParser.payment_parser().parse_promo_code(promo_code_orm=promo_code_orm)

    # ------------------------ Update PMUserPlan resource --------------------- #
    def update_promo_code_remaining_times(self, promo_code: PromoCode, amount: int = 1) -> PromoCode:
        promo_code_orm = self._get_promo_code_orm(promo_code_id=promo_code.promo_code_id)
        promo_code_orm.remaining_times = F('remaining_times') - 1
        promo_code_orm.save()
        promo_code_orm.refresh_from_db()
        return ModelParser.payment_parser().parse_promo_code(promo_code_orm=promo_code_orm)

    # ------------------------ Delete PMUserPlan resource --------------------- #

