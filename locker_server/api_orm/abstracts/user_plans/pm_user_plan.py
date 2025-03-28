from django.db import models

from locker_server.settings import locker_server_settings
from locker_server.shared.constants.transactions import *


class AbstractPMUserPlanORM(models.Model):
    user = models.OneToOneField(
        locker_server_settings.LS_USER_MODEL, to_field='user_id',
        primary_key=True, related_name="pm_user_plan", on_delete=models.CASCADE
    )
    duration = models.CharField(max_length=128, default=DURATION_MONTHLY)
    start_period = models.FloatField(null=True, default=None)
    end_period = models.FloatField(null=True, default=None)
    cancel_at_period_end = models.BooleanField(default=False)
    custom_endtime = models.FloatField(null=True, default=None)  # Custom endtime for some special cases
    default_payment_method = models.CharField(max_length=128, default=PAYMENT_METHOD_CARD)

    ref_plan_code = models.CharField(max_length=128, null=True, default=None)
    number_members = models.IntegerField(default=1)                 # Number of member business
    personal_trial_applied = models.BooleanField(default=False)     # Did this user apply the personal trial plan?
    enterprise_trial_applied = models.BooleanField(default=False)   # Did this user apply the enterprise plan?
    personal_trial_mobile_applied = models.BooleanField(default=False)
    personal_trial_web_applied = models.BooleanField(default=False)
    pm_stripe_subscription = models.CharField(max_length=255, null=True)
    pm_stripe_subscription_created_time = models.IntegerField(null=True)
    pm_mobile_subscription = models.CharField(max_length=255, null=True, default=None)
    saas_license = models.CharField(max_length=64, unique=True, null=True, default=None)

    extra_time = models.IntegerField(default=0)
    extra_plan = models.CharField(max_length=128, null=True, default=None)
    member_billing_updated_time = models.FloatField(null=True, default=None)

    attempts = models.IntegerField(default=0)

    pm_plan = models.ForeignKey(
        locker_server_settings.LS_PLAN_MODEL, on_delete=models.CASCADE, related_name="pm_user_plan"
    )
    promo_code = models.ForeignKey(
        locker_server_settings.LS_PROMO_CODE_MODEL, on_delete=models.SET_NULL, related_name="pm_user_plans",
        null=True, default=None
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['pm_mobile_subscription', ]),
        ]

    @classmethod
    def update_or_create(cls, user, pm_plan_alias=PLAN_TYPE_PM_FREE, duration=DURATION_MONTHLY):
        """
        Create plan object
        :param user: (obj) User object
        :param pm_plan_alias: (str) PM plan alias
        :param duration: (str) duration of this plan
        :return:
        """
        raise NotImplementedError

    # @classmethod
    # def get_next_attempts_duration(cls, current_number_attempts):
    #     if current_number_attempts < 2:
    #         return 86400
    #     return 86400 * 3
    # 
    # @classmethod
    # def get_next_attempts_day_str(cls, current_number_attempts):
    #     if current_number_attempts < 2:
    #         return "1 day from today"
    #     return "3 days from today"
    # 
    # def get_plan_obj(self):
    #     return self.pm_plan
    # 
    # def get_plan_type_alias(self) -> str:
    #     return self.get_plan_obj().get_alias()
    # 
    # def get_plan_type_name(self) -> str:
    #     return self.get_plan_obj().get_name()
    # 
    # def is_subscription(self):
    #     stripe_subscription = self.get_stripe_subscription()
    #     if stripe_subscription:
    #         return True if stripe_subscription.cancel_at_period_end is False else False
    #     if self.start_period and self.end_period and self.end_period >= now():
    #         return True
    #     return False
    # 
    # def is_trailing(self):
    #     stripe_subscription = self.get_stripe_subscription()
    #     if stripe_subscription:
    #         return stripe_subscription.status == "trialing"
    #     mobile_subscription = self.pm_mobile_subscription
    #     return self.start_period and self.end_period and self.personal_trial_applied and mobile_subscription is None
    # 
    # def is_cancel_at_period_end(self) -> bool:
    #     stripe_subscription = self.get_stripe_subscription()
    #     if stripe_subscription:
    #         return stripe_subscription.cancel_at_period_end
    #     return self.cancel_at_period_end
    # 
    # def get_subscription(self):
    #     """
    #     Get subscription object of this plan
    #     :return:
    #     """
    #     stripe_subscription = self.get_stripe_subscription()
    #     if stripe_subscription:
    #         return True if stripe_subscription.cancel_at_period_end is False else False
    #     if self.start_period and self.end_period and self.end_period >= now():
    #         return True
    #     return False
    # 
    # def get_stripe_subscription(self):
    #     """
    #     Get Stripe Subscription object
    #     :return:
    #     """
    #     if not self.pm_stripe_subscription:
    #         return None
    #     return stripe.Subscription.retrieve(self.pm_stripe_subscription)
    # 
    # def cancel_stripe_subscription(self):
    #     """
    #     Cancel Stripe subscription
    #     :return:
    #     """
    #     self.pm_stripe_subscription = None
    #     self.pm_stripe_subscription_created_time = None
    #     self.promo_code = None
    #     self.save()
    # 
    def cancel_mobile_subscription(self):
        # Set mobile subscription to Null
        self.promo_code = None
        # self.pm_mobile_subscription = None
        self.save()
    # 
    # def get_next_billing_time(self, duration=None):
    #     """
    #     Get next billing time of this plan
    #     :param duration:
    #     :return:
    #     """
    #     # if this plan is not subscription plan => Return None
    #     plan_alias = self.get_plan_type_alias()
    #     if plan_alias in [PLAN_TYPE_PM_FREE]:
    #         return None
    #     # If this plan is lifetime => return end_period (None)
    #     if plan_alias in [PLAN_TYPE_PM_LIFETIME]:
    #         return self.end_period
    #     # If subscription object is None => Get next billing time of this user plan
    #     stripe_subscription = self.get_stripe_subscription()
    #     if stripe_subscription:
    #         if stripe_subscription.status == "trialing":
    #             return stripe_subscription.trial_end
    #         return stripe_subscription.current_period_end
    # 
    #     # If user subscribed a plan
    #     if self.end_period:
    #         return self.end_period
    #     # User is not still subscribe any subscription
    #     return now() + Payment.get_duration_month_number(duration=duration) * 30 * 86400
    # 
    # def get_next_retry_payment_date(self, stripe_subscription=None):
    #     if self.get_plan_type_alias() in [PLAN_TYPE_PM_FREE]:
    #         return None
    #     # Retrieve Stripe subscription object
    #     if not stripe_subscription:
    #         stripe_subscription = self.get_stripe_subscription()
    #     if stripe_subscription:
    #         if stripe_subscription.status not in [PAYMENT_STATUS_PAST_DUE]:
    #             return None
    #         latest_invoice = stripe_subscription.latest_invoice
    #         if not latest_invoice:
    #             return None
    #         latest_invoice_obj = stripe.Invoice.retrieve(latest_invoice)
    #         return latest_invoice_obj.next_payment_attempt
    #     if self.attempts > 0:
    #         return PMUserPlan.get_next_attempts_duration(
    #             current_number_attempts=self.attempts
    #         ) + self.end_period
    # 
    # def get_current_number_members(self):
    #     return self.number_members
    # 
    # def get_max_allow_members(self):
    #     plan_obj = self.get_plan_obj()
    #     if plan_obj.is_team_plan:
    #         return self.number_members
    #     return plan_obj.get_max_number_members()
    # 
    # def set_default_payment_method(self, method):
    #     self.default_payment_method = method
    #     self.save()
    # 
    # def get_default_payment_method(self):
    #     return self.default_payment_method
    # 
    # def calc_difference_price(self, new_plan, new_duration, currency):
    #     """
    #     Calc difference price when upgrade plan
    #     :param new_plan: (obj)
    #     :param new_duration: (str)
    #     :param currency: (str)
    #     :return:
    #     """
    # 
    # def calc_update_price(self, new_plan, new_duration, new_quantity, currency, promo_code=None):
    #     """
    #     Calc amount when user update plan (via upgrade plan or change quantity)
    #     :param new_plan: (obj) Plan object
    #     :param new_duration: (str) New duration: monthly/half_yearly/yearly
    #     :param new_quantity: (int) New number of quantity
    #     :param currency: (str) Currency
    #     :param promo_code: (str) Promo code string value
    #     :return:
    #     """
    #     current_time = now()
    #     # Get new plan price
    #     new_plan_price = new_plan.get_price(duration=new_duration, currency=currency)
    #     # Number of month duration billing by new duration
    #     duration_next_billing_month = Payment.get_duration_month_number(new_duration)
    #     # Calc discount
    #     error_promo = None
    #     promo_code_obj = None
    #     promo_description_en = None
    #     promo_description_vi = None
    #     if promo_code is not None and promo_code != "":
    #         promo_code_obj = PromoCode.check_valid(value=promo_code, current_user=self.user, new_duration=new_duration)
    #         if not promo_code_obj:
    #             error_promo = {"promo_code": ["This coupon is expired or incorrect"]}
    #         else:
    #             # if not (new_duration == DURATION_YEARLY and promo_code_obj.duration < 12):
    #             #     duration_next_billing_month = promo_code_obj.duration
    #             promo_description_en = promo_code_obj.description_en
    #             promo_description_vi = promo_code_obj.description_vi
    # 
    #     # If user subscribes by Stripe => Using Stripe service
    #     # if self.pm_stripe_subscription:
    #     #     from cystack_models.factory.payment_method.payment_method_factory import PaymentMethodFactory
    #     #     total_amount, next_billing_time = PaymentMethodFactory.get_method(
    #     #         user=self.user, scope=settings.SCOPE_PWD_MANAGER, payment_method=PAYMENT_METHOD_CARD
    #     #     ).calc_update_total_amount(new_plan=new_plan, new_duration=new_duration, new_quantity=new_quantity)
    #     # # Else, calc manually
    #     # else:
    #     #     # Calc immediate amount and next billing time
    #     #     # If this is the first time user register subscription
    #     #     if not self.end_period or not self.start_period:
    #     #         # Diff_price is price of the plan that user will subscribe
    #     #         total_amount = new_plan_price * new_quantity
    #     #         next_billing_time = self.get_next_billing_time(duration=new_duration)
    #     #     # Else, update the existed subscription
    #     #     else:
    #     #         # Calc old amount with discount
    #     #         old_price = self.pm_plan.get_price(duration=self.duration, currency=currency)
    #     #         old_amount = old_price * self.number_members
    #     #         if self.promo_code:
    #     #             discount = self.promo_code.get_discount(old_amount, duration=self.duration)
    #     #             old_amount = old_amount - discount
    #     #         # If new plan has same duration, next billing time does not change
    #     #         # Money used: (now - start) / (end - start) * old_price
    #     #         # Money remain: old_price - money_used
    #     #         # => Diff price: new_price - money_remain
    #     #         if self.duration == new_duration:
    #     #             old_remain = old_amount * (
    #     #                     1 - (current_time - self.start_period) / (self.end_period - self.start_period)
    #     #             )
    #     #             new_remain = new_plan_price * new_quantity * (
    #     #                     (self.end_period - current_time) / (self.end_period - self.start_period)
    #     #             )
    #     #             total_amount = new_remain - old_remain
    #     #             next_billing_time = self.get_next_billing_time(duration=new_duration)
    #     #         # Else, new plan has difference duration, the start of plan will be restarted
    #     #         else:
    #     #             old_used = old_amount * (
    #     #                     (current_time - self.start_period) / (self.end_period - self.start_period)
    #     #             )
    #     #             old_remain = old_amount - old_used
    #     #             total_amount = new_plan_price * new_quantity - old_remain
    #     #             next_billing_time = current_time + duration_next_billing_month * 30 * 86400
    # 
    #     total_amount = new_plan_price * new_quantity
    #     next_billing_time = current_time + duration_next_billing_month * 30 * 86400
    # 
    #     # Discount and immediate payment
    #     total_amount = max(total_amount, 0)
    #     discount = promo_code_obj.get_discount(total_amount, duration=new_duration) if promo_code_obj else 0.0
    #     immediate_amount = max(round(total_amount - discount, 2), 0)
    # 
    #     result = {
    #         "alias": new_plan.get_alias(),
    #         "price": round(new_plan_price, 2),
    #         "total_price": total_amount,
    #         "discount": discount,
    #         "duration": new_duration,
    #         "currency": currency,
    #         "immediate_payment": immediate_amount,
    #         "next_billing_time": next_billing_time,
    #         "personal_trial_applied": self.is_personal_trial_applied(),
    #         "promo_description": {
    #             "en": promo_description_en,
    #             "vi": promo_description_vi
    #         },
    #         "error_promo": error_promo
    #     }
    # 
    #     if new_plan.is_team_plan is False:
    #         if self.is_personal_trial_applied() is False:
    #             utm_source = self.user.get_from_cystack_id().get("utm_source")
    #             if utm_source in LIST_UTM_SOURCE_PROMOTIONS:
    #                 result["next_billing_time"] = next_billing_time + TRIAL_PERSONAL_PLAN
    #             else:
    #                 result["next_billing_time"] = now() + TRIAL_PERSONAL_PLAN
    #                 result["next_billing_payment"] = immediate_amount
    #                 result["immediate_payment"] = 0
    #     else:
    #         if self.end_period and self.end_period > now():
    #             result["next_billing_time"] = self.end_period
    #             result["next_billing_payment"] = immediate_amount
    #             result["immediate_payment"] = 0
    #     return result
    # 
    # def calc_current_payment_price(self, currency):
    #     plan_price = self.pm_plan.get_price(duration=self.duration, currency=currency)
    #     total_price = plan_price * self.number_members
    #     # Calc discount
    #     discount = 0.0
    #     if self.promo_code is not None:
    #         # If the promo code of this plan is still available
    #         max_promo_period = self.promo_code.get_number_applied_period(duration=self.duration)
    #         if self.user.payments.filter(promo_code=self.promo_code).count() < max_promo_period:
    #             discount = self.promo_code.get_discount(total_price, duration=self.duration)
    #         # Else, remove promo code
    #         else:
    #             self.promo_code = None
    #             self.save()
    # 
    #     current_amount = max(round(total_price - discount, 2), 0)
    #     return current_amount
    # 
    # def is_personal_trial_applied(self) -> bool:
    #     return self.personal_trial_applied
    # 
    # def is_enterprise_trial_applied(self) -> bool:
    #     return self.enterprise_trial_applied
    # 
    # def is_update_personal_to_enterprise(self, new_plan_alias) -> bool:
    #     """
    #     Handle event hooks: The plan update event is a personal plan while the current plan is Enterprise plan
    #     So, we don't need to update the plan of this user
    #     :param new_plan_alias: (str) Event hook plan
    #     :return:
    #     True - Event hook is personal plan. Current plan is Enterprise
    #     """
    #     try:
    #         new_plan_obj = PMPlan.objects.get(alias=new_plan_alias)
    #         if self.get_plan_obj().is_team_plan is True and new_plan_obj.is_team_plan is False:
    #             return True
    #     except PMPlan.DoesNotExist:
    #         pass
    #     return False
