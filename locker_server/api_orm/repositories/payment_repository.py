import logging
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import stripe
import stripe.error

from django.db.models import F, OuterRef, Subquery, FloatField, CharField, Q, Sum, DateTimeField, Count
from django.db.models.expressions import RawSQL, Case, When
from django.db.models.functions import TruncYear

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models import CustomerORM
from locker_server.api_orm.models.wrapper import get_payment_model, get_promo_code_model, get_user_model, \
    get_user_plan_model, get_plan_model
from locker_server.api_orm.repositories import UserORMRepository
from locker_server.core.entities.payment.payment import Payment
from locker_server.core.entities.payment.promo_code import PromoCode
from locker_server.core.repositories.payment_repository import PaymentRepository
from locker_server.shared.constants.transactions import *
from locker_server.shared.utils.app import now, random_n_digit

PaymentORM = get_payment_model()
UserORM = get_user_model()
PromoCodeORM = get_promo_code_model()
PMUserPlanORM = get_user_plan_model()
PMPlanORM = get_plan_model()
ModelParser = get_model_parser()


class PaymentORMRepository(PaymentRepository):
    @staticmethod
    def _generate_duration_init_data(start, end, duration="monthly"):
        durations_list = []
        for i in range((end - start).days + 1):
            date = start + timedelta(days=i)
            if duration == "daily":
                d = "{}-{:02}-{:02}".format(date.year, date.month, date.day)
            elif duration == "weekly":
                d = date.isocalendar()[:2]  # e.g. (2022, 24)
                d = "{}-{:02}".format(*d)
            elif duration == "monthly":
                d = "{}-{:02}".format(date.year, date.month)
            else:
                d = "{}".format(date.year)
            durations_list.append(d)
        duration_init = dict()
        for d in sorted(set(durations_list), reverse=True):
            duration_init[d] = {}

        # # Get annotation query
        if duration == "daily":
            query = "CONCAT(YEAR(FROM_UNIXTIME(created_time)), '-', " \
                    "LPAD(MONTH(FROM_UNIXTIME(created_time)), 2, '0'), '-', " \
                    "LPAD(DAY(FROM_UNIXTIME(created_time)), 2, '0') )"
        elif duration == "weekly":
            query = "CONCAT(YEAR(FROM_UNIXTIME(created_time)), '-', LPAD(WEEK(FROM_UNIXTIME(created_time)), 2, '0'))"
        elif duration == "monthly":
            query = "CONCAT(YEAR(FROM_UNIXTIME(created_time)), '-', LPAD(MONTH(FROM_UNIXTIME(created_time)), 2, '0'))"
        else:
            query = "YEAR(FROM_UNIXTIME(created_time))"
        return {
            "duration_init": duration_init,
            "query": query
        }

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

    @classmethod
    def list_payments_orm(cls, **filters) -> List[PaymentORM]:
        from_param = filters.get("from")
        to_param = filters.get("to")
        platform_param = filters.get("platform", "")  # CHPlay,Stripe,ChPlay, Markets
        status_param = filters.get("status")  # success,failed,pending
        plan_param = filters.get("plan")  # premium, lifetime,family,enterprise
        utm_source_param = filters.get("utm_source")  # organic,ads, affiliate
        payment_method_param = filters.get("payment_method")
        user_id_param = filters.get("user_id")
        enterprise_id_param = filters.get("enterprise_id")

        # Filter
        payments_orm = PaymentORM.objects.all()

        if from_param:
            payments_orm = payments_orm.filter(created_time__gt=from_param)
        if to_param:
            payments_orm = payments_orm.filter(created_time__lte=to_param)

        if plan_param:
            payments_orm = payments_orm.filter(plan=plan_param)
        if status_param:
            payments_orm = payments_orm.filter(status=status_param)
        if utm_source_param:
            user_ids = UserORMRepository.search_from_cystack_id(**{"utm_source": utm_source_param}).get("ids", [])
            payments_orm = payments_orm.filter(user_id__in=user_ids)
        if platform_param:
            platform_param = platform_param.lower()
            if platform_param == "stripe":
                payments_orm = payments_orm.filter(stripe_invoice_id__isnull=False)
            elif platform_param == "ios":
                payments_orm = payments_orm.filter(
                    Q(stripe_invoice_id__isnull=True) & Q(metadata__contains="ios") & Q(mobile_invoice_id__isnull=False)

                )
            elif platform_param == "android":
                payments_orm = payments_orm.filter(
                    Q(stripe_invoice_id__isnull=True) & Q(metadata__contains="android") &
                    Q(mobile_invoice_id__isnull=False)

                )
        if payment_method_param:
            payments_orm = payments_orm.filter(payment_method=payment_method_param)
        if user_id_param:
            payments_orm = payments_orm.filter(user_id=user_id_param)
        if enterprise_id_param:
            payments_orm = payments_orm.filter(enterprise_id=enterprise_id_param)

        payments_orm = payments_orm.select_related('user')
        payments_orm = payments_orm.order_by("-created_time")
        return payments_orm

    # ------------------------ List Payment resource ------------------- #
    def list_all_invoices(self, **filter_params) -> List[Payment]:
        payments_orm = self.list_payments_orm(**filter_params)
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

    def list_feedback_after_subscription(self, after_days: int = 30) -> List[Dict]:
        payments_orm = PaymentORM.objects.filter(
            user_id=OuterRef("user_id"), total_price__gt=0,
            status=PAYMENT_STATUS_PAID
        ).order_by('created_time')
        users_feedback = UserORM.objects.filter(activated=True).annotate(
            first_payment_date=Subquery(payments_orm.values('created_time')[:1], output_field=FloatField()),
            first_payment_plan=Subquery(payments_orm.values('plan')[:1], output_field=CharField()),
        ).exclude(first_payment_date__isnull=True).filter(
            first_payment_date__gte=now() - after_days * 86400,
            first_payment_date__lt=now() - (after_days - 1) * 86400
        ).values('user_id', 'first_payment_plan')
        return users_feedback

    def statistic_income(self, **filters) -> Dict:
        from_param = filters.get("from")
        to_param = filters.get("to")
        if to_param is None:
            to_param = now()
        if from_param is None:
            from_param = PaymentORM.objects.first().created_time
        filters.update({
            "from": from_param,
            "to": to_param
        })
        filters.pop("status", None)
        payments_orm = self.list_payments_orm(**filters)

        # remove testing payment
        exclude_user_ids = []
        payments_orm = payments_orm.exclude(
            user_id__in=exclude_user_ids
        ).filter(
            payment_id__startswith="LK"
        )
        success_payments_orm = payments_orm.filter(
            status="paid"
        )

        # statistic income by duration
        duration_param = filters.get("duration")
        duration_init_data = self._generate_duration_init_data(
            start=datetime.fromtimestamp(from_param),
            end=datetime.fromtimestamp(to_param),
            duration=duration_param
        )
        gross_payment_statistic = duration_init_data.get("duration_init") or {}
        query = duration_init_data.get("query")

        gross_payments_orm_by_duration = success_payments_orm.annotate(
            duration_pivot=RawSQL(query, [], output_field=CharField())
        ).values("duration_pivot", "currency").annotate(total_price=Sum(F("total_price"))).order_by(
            "currency", "duration_pivot")
        for payment_orm_by_duration in gross_payments_orm_by_duration:
            duration_pivot = str(payment_orm_by_duration.get("duration_pivot"))
            duration_data = gross_payment_statistic.get(duration_pivot) or {}
            duration_data.update({
                payment_orm_by_duration.get("currency"): payment_orm_by_duration.get("total_price")
            })
            gross_payment_statistic[duration_pivot] = duration_data

        total_gross = success_payments_orm.values("currency").annotate(
            total_price=Sum(F('total_price'))
        ).order_by("currency")

        # Statistic by status
        payments_orm_by_status = payments_orm.values("status", "currency").annotate(
            total_price=Sum('total_price')
        ).order_by('status', 'currency')
        payment_by_status_statistic = {}
        for item in payments_orm_by_status:
            status_dict = payment_by_status_statistic.get(item.get("status")) or {}
            status_dict.update({
                item.get('currency'): item.get("total_price")
            })
            payment_by_status_statistic[item.get("status")] = status_dict
        total_payment_orm = payments_orm.values("currency").annotate(
            total_price=Sum(F('total_price'))
        ).order_by("currency")
        result = {
            "total_gross": {
                item.get("currency"): item.get("total_price")
                for item in total_gross
            },
            "gross_by_duration": gross_payment_statistic,
            "total_payment": {
                item.get("currency"): item.get("total_price")
                for item in total_payment_orm
            },
            "payment_by_status": payment_by_status_statistic
        }
        return result

    def statistic_amount(self, **filters) -> Dict:
        from_param = filters.get("from")
        to_param = filters.get("to")
        if to_param is None:
            to_param = now()
        if from_param is None:
            from_param = PaymentORM.objects.first().created_time
        filters.update({
            "from": from_param,
            "to": to_param
        })
        filters.pop("status", None)
        payments_orm = self.list_payments_orm(**filters)

        # remove testing user id and failed payment
        exclude_user_ids = []
        payments_orm = payments_orm.exclude(
            user_id__in=exclude_user_ids
        ).filter(
            payment_id__startswith="LK"
        )
        success_payments_orm = payments_orm.filter(
            status="paid",
        )

        # statistic volume by duration
        duration_param = filters.get("duration")
        duration_init_data = self._generate_duration_init_data(
            start=datetime.fromtimestamp(from_param),
            end=datetime.fromtimestamp(to_param),
            duration=duration_param
        )
        payment_by_duration_statistic = duration_init_data.get("duration_init") or {}
        query = duration_init_data.get("query")

        payments_orm_by_duration = success_payments_orm.annotate(
            duration_pivot=RawSQL(query, [], output_field=CharField())
        ).values("duration_pivot", "currency").annotate(volume=Count('duration_pivot')).order_by(
            "currency", "duration_pivot")
        for payment_by_duration in payments_orm_by_duration:
            duration_pivot = str(payment_by_duration.get("duration_pivot"))
            duration_data = payment_by_duration_statistic.get(duration_pivot) or {}
            duration_data.update({
                payment_by_duration.get("currency"): payment_by_duration.get("volume")
            })
            payment_by_duration_statistic[duration_pivot] = duration_data

        total_volume = success_payments_orm.values("currency").annotate(
            volume=Count('total_price')
        ).order_by("currency")

        # Statistic by status
        payments_orm_by_status = payments_orm.values("status", "currency").annotate(
            volume=Count('total_price')
        ).order_by('status', 'currency')
        payment_by_status_statistic = {}
        for item in payments_orm_by_status:
            status_dict = payment_by_status_statistic.get(item.get("status")) or {}
            status_dict.update({
                item.get('currency'): item.get("volume")
            })
            payment_by_status_statistic[item.get("status")] = status_dict
        total_payment_orm = payments_orm.values("currency").annotate(
            volume=Count('total_price')
        ).order_by("currency")
        result = {
            "total_success_amount": {
                item.get("currency"): item.get("volume")
                for item in total_volume
            },
            "success_amount_by_duration": payment_by_duration_statistic,
            "total_amount": {
                item.get("currency"): item.get("volume")
                for item in total_payment_orm
            },
            "amount_by_status": payment_by_status_statistic
        }
        return result

    def statistic_by_type(self, **filters) -> List:
        payments_orm = self.list_payments_orm(**filters)
        by_param = filters.get("by")
        statistic_dict = {}
        if by_param == "plan":
            payments_orm_by_plan = payments_orm.values("plan", "currency").annotate(
                total_price=Sum(F("total_price"))
            ).order_by("plan", "currency")
            for result in payments_orm_by_plan:
                plan_key = result.get("plan")
                plan_dict = statistic_dict.get(plan_key) or {}
                plan_dict.update({
                    result.get("currency"): result.get("total_price")
                })
                statistic_dict[plan_key] = plan_dict
        elif by_param == "status":
            payments_orm_by_status = payments_orm.values("status", "currency").annotate(
                total_price=Sum(F("total_price"))
            ).order_by("status", "currency")
            for result in payments_orm_by_status:
                key = result.get("status")
                values = statistic_dict.get(key) or {}
                values.update({
                    result.get("currency"): result.get("total_price")
                })
                statistic_dict[key] = values
        elif by_param == "platform":
            total_price_stripe = payments_orm.filter(stripe_invoice_id__isnull=False).values("currency").annotate(
                total_price=Sum('total_price')
            ).order_by("currency")

            total_price_ios = payments_orm.filter(
                Q(stripe_invoice_id__isnull=True) & Q(metadata__contains="ios") & Q(mobile_invoice_id__isnull=False)
            ).values("currency").annotate(
                total_price=Sum('total_price')
            ).order_by("currency")
            total_price_android = payments_orm.filter(
                Q(stripe_invoice_id__isnull=True) & Q(metadata__contains="android") &
                Q(mobile_invoice_id__isnull=False)
            ).values("currency").annotate(
                total_price=Sum('total_price')
            ).order_by("currency")

            stripe_dict = {item.get("currency"): item.get("total_price") for item in total_price_stripe}
            ios_dict = {item.get("currency"): item.get("total_price") for item in total_price_ios}
            android_dict = {item.get("currency"): item.get("total_price") for item in total_price_android}

            statistic_dict = {
                "ios": ios_dict,
                "stripe": stripe_dict,
                "android": android_dict
            }

        return [{"type": k, "value": v} for k, v in statistic_dict.items()]

    # ------------------------ Get Payment resource --------------------- #
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

    def get_by_mobile_invoice_id(self, mobile_invoice_id: str) -> Optional[Payment]:
        payment_orm = PaymentORM.objects.filter(mobile_invoice_id=mobile_invoice_id).first()
        return ModelParser.payment_parser().parse_payment(payment_orm=payment_orm) if payment_orm else None

    def get_by_stripe_invoice_id(self, stripe_invoice_id: str) -> Optional[Payment]:
        payment_orm = PaymentORM.objects.filter(stripe_invoice_id=stripe_invoice_id).first()
        return ModelParser.payment_parser().parse_payment(payment_orm=payment_orm) if payment_orm else None

    def get_by_banking_code(self, code: str) -> Optional[Payment]:
        try:
            payment_orm = PaymentORM.objects.get(code=code)
            return ModelParser.payment_parser().parse_payment(payment_orm=payment_orm)
        except PaymentORM.DoesNotExist:
            return None

    def check_saas_promo_code(self, user_id: int, code: str) -> Optional[PromoCode]:
        user_orm = self._get_user_orm(user_id=user_id)
        if not user_orm:
            return None
        promo_code_orm = PromoCodeORM.check_saas_valid(value=code, current_user=user_orm)
        if not promo_code_orm:
            return None
        return ModelParser.payment_parser().parse_promo_code(promo_code_orm=promo_code_orm)

    def check_promo_code(self, user_id: int, code: str, new_duration: str = None,
                         new_plan: str = None) -> Optional[PromoCode]:
        user_orm = self._get_user_orm(user_id=user_id)
        if not user_orm:
            return None
        promo_code_orm = PromoCodeORM.check_valid(
            value=code, current_user=user_orm, new_duration=new_duration, new_plan=new_plan
        )
        if not promo_code_orm:
            return None
        return ModelParser.payment_parser().parse_promo_code(promo_code_orm=promo_code_orm)

    def count_referral_payments(self, referral_user_ids: List[int]) -> int:
        return PaymentORM.objects.filter(
            status__in=[PAYMENT_STATUS_PAID], user_id__in=referral_user_ids
        ).count()

    def is_first_payment(self, user_id: int, **filter_params) -> bool:
        exclude_total_0 = filter_params.get("exclude_total_0", True)
        plans_param = filter_params.get("plans", [])
        durations_param = filter_params.get("durations", [])
        status_param = filter_params.get("status")
        payments = PaymentORM.objects.filter(user_id=user_id)
        if exclude_total_0 is True:
            payments = payments.exclude(total_price=0)
        if plans_param and durations_param:
            payments = payments.filter(plan__in=plans_param, duration__in=durations_param)
        if status_param:
            payments = payments.filter(status=status_param)
        #     if plans_param:
        #         payments = payments.filter(plan__in=plans_param)
        #     if durations:
        #         payments = payments.filter(duration__in=durations)
        return payments.count() == 1

    # ------------------------ Create Payment resource --------------------- #
    def create_payment(self, **payment_data) -> Optional[Payment]:
        payment_orm = PaymentORM.create(**payment_data)
        # Set promo code and customer
        promo_code = payment_data.get("promo_code", None)
        payment_orm = self.__set_promo_code(payment_orm=payment_orm, promo_code=promo_code)
        # Set customer
        customer = payment_data.get('customer', None)
        payment_orm = self.__set_customer(payment_orm=payment_orm, customer=customer)
        # Create payment items
        payment_orm = self.__set_payment_items(payment_orm, **payment_data)
        # Set total price
        total_price = payment_data.get("total_price")
        if total_price is None:
            payment_orm = self.__set_total_price(payment_orm)
        else:
            payment_orm.total_price = total_price
            payment_orm.save()
        # Set banking code
        payment_orm = self.__set_banking_code(payment_orm=payment_orm, bank_id=payment_data.get("bank_id"))

        return ModelParser.payment_parser().parse_payment(payment_orm=payment_orm)

    @staticmethod
    def __set_promo_code(payment_orm: PaymentORM, promo_code: str = None):
        if promo_code is None:
            payment_orm.promo_code = None
        else:
            try:
                promo_orm = PromoCodeORM.objects.get(id=promo_code)
                payment_orm.promo_code = promo_orm
                promo_orm.remaining_times = F('remaining_times') - 1
                promo_orm.save()
            except PromoCodeORM.DoesNotExist:
                payment_orm.promo_code = None
        payment_orm.save()
        return payment_orm

    @staticmethod
    def __set_customer(payment_orm: PaymentORM, customer=None):
        if customer is None:
            payment_orm.customer = None
        else:
            new_customer = CustomerORM.create(**customer)
            payment_orm.customer = new_customer
        payment_orm.save()
        return payment_orm

    @staticmethod
    def __set_payment_items(payment_orm: PaymentORM, **data):
        payments_items = data.get("payment_items", [])
        payment_orm.payment_items.model.create_multiple(payment_orm, *payments_items)
        return payment_orm

    @staticmethod
    def __set_total_price(payment_orm: PaymentORM):
        # Get total price without discount
        number = int(payment_orm.get_metadata().get("number_members", 1))
        plan_price = PMPlanORM.objects.get(alias=payment_orm.plan).get_price(
            duration=payment_orm.duration, currency=payment_orm.currency
        )
        payment_orm.total_price = plan_price * number
        # Get discount here
        if payment_orm.promo_code is not None:
            payment_orm.discount = payment_orm.promo_code.get_discount(
                payment_orm.total_price, duration=payment_orm.duration
            )
        # Finally, calc total price
        payment_orm.total_price = max(round(payment_orm.total_price - payment_orm.discount, 2), 0)
        payment_orm.save()
        return payment_orm

    @staticmethod
    def __set_banking_code(payment_orm: PaymentORM, bank_id=None):
        # Set banking code
        if payment_orm.payment_method == PAYMENT_METHOD_BANKING:
            payment_orm.code = "{}{}".format(BANKING_ID_PWD_MANAGER, 10000 + payment_orm.id)
            payment_orm.bank_id = bank_id
            payment_orm.save()
        return payment_orm

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

    # ------------------------ Update Payment resource --------------------- #
    def update_promo_code_remaining_times(self, promo_code: PromoCode, amount: int = 1) -> PromoCode:
        promo_code_orm = self._get_promo_code_orm(promo_code_id=promo_code.promo_code_id)
        promo_code_orm.remaining_times = F('remaining_times') - 1
        promo_code_orm.save()
        promo_code_orm.refresh_from_db()
        return ModelParser.payment_parser().parse_promo_code(promo_code_orm=promo_code_orm)

    def update_payment(self, payment: Payment, update_data) -> Payment:
        payment_orm = self._get_payment_orm(payment_id=payment.payment_id)
        payment_orm.total_price = update_data.get("total_price", payment_orm.total_price)
        payment_orm.discount = update_data.get("discount", payment_orm.discount)
        payment_orm.transaction_type = update_data.get("transaction_type", payment_orm.transaction_type)
        payment_orm.stripe_invoice_id = update_data.get("stripe_invoice_id", payment_orm.stripe_invoice_id)
        payment_orm.status = update_data.get("status", payment_orm.status)
        payment_orm.save()
        return ModelParser.payment_parser().parse_payment(payment_orm=payment_orm)

    def set_paid(self, payment: Payment) -> Payment:
        payment_orm = self._get_payment_orm(payment_id=payment.payment_id)
        payment_orm.status = PAYMENT_STATUS_PAID
        payment_orm.failure_reason = None
        payment_orm.save()
        # Set paid
        payment.status = PAYMENT_STATUS_PAID
        payment.failure_reason = None
        return payment

    def set_past_due(self, payment: Payment, failure_reason=None) -> Payment:
        payment_orm = self._get_payment_orm(payment_id=payment.payment_id)
        payment_orm.failure_reason = failure_reason
        payment_orm.status = PAYMENT_STATUS_PAST_DUE
        payment_orm.save()
        # Set
        payment.failure_reason = failure_reason
        payment.status = PAYMENT_STATUS_PAST_DUE
        return payment

    def set_failed(self, payment: Payment, failure_reason=None):
        payment_orm = self._get_payment_orm(payment_id=payment.payment_id)
        payment_orm.failure_reason = failure_reason
        payment_orm.status = PAYMENT_STATUS_FAILED
        payment_orm.save()
        # Set
        payment.failure_reason = failure_reason
        payment.status = PAYMENT_STATUS_FAILED
        return payment

    # ------------------------ Delete Payment resource --------------------- #
