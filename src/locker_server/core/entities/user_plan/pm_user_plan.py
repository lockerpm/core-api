import stripe

from locker_server.core.entities.payment.promo_code import PromoCode
from locker_server.core.entities.user.user import User
from locker_server.core.entities.user_plan.pm_plan import PMPlan
from locker_server.shared.constants.transactions import DURATION_MONTHLY, PAYMENT_METHOD_CARD


class PMUserPlan(object):
    def __init__(self, pm_user_plan_id: int, user: User, duration: str = DURATION_MONTHLY, start_period: float = None,
                 end_period: float = None, cancel_at_period_end: bool = False, custom_endtime: float = None,
                 default_payment_method: str = PAYMENT_METHOD_CARD, ref_plan_code: str = None, number_members: int = 1,
                 personal_trial_applied: bool = False, enterprise_trial_applied: bool = False,
                 personal_trial_mobile_applied: bool = False, personal_trial_web_applied: bool = False,
                 pm_stripe_subscription: str = None, pm_stripe_subscription_created_time: int = None,
                 pm_mobile_subscription: str = None, extra_time: int = 0, extra_plan: str = None,
                 member_billing_updated_time: float = None, attempts: int = 0, pm_plan: PMPlan = None,
                 promo_code: PromoCode = None):

        self._pm_user_plan_id = pm_user_plan_id
        self._user = user
        self._duration = duration
        self._start_period = start_period
        self._end_period = end_period
        self._cancel_at_period_end = cancel_at_period_end
        self._custom_endtime = custom_endtime
        self._default_payment_method = default_payment_method
        self._ref_plan_code = ref_plan_code
        self._number_members = number_members
        self._personal_trial_applied = personal_trial_applied
        self._enterprise_trial_applied = enterprise_trial_applied
        self._personal_trial_mobile_applied = personal_trial_mobile_applied
        self._personal_trial_web_applied = personal_trial_web_applied
        self._pm_stripe_subscription = pm_stripe_subscription
        self._pm_stripe_subscription_created_time = pm_stripe_subscription_created_time
        self._pm_mobile_subscription = pm_mobile_subscription
        self._extra_time = extra_time
        self._extra_plan = extra_plan
        self._member_billing_updated_time = member_billing_updated_time
        self._attempts = attempts
        self._pm_plan = pm_plan
        self._promo_code = promo_code

    @property
    def pm_user_plan_id(self):
        return self._pm_user_plan_id

    @property
    def user(self):
        return self._user

    @property
    def duration(self):
        return self._duration

    @property
    def start_period(self):
        return self._start_period

    @property
    def end_period(self):
        return self._end_period

    @property
    def cancel_at_period_end(self):
        return self._cancel_at_period_end

    @property
    def custom_endtime(self):
        return self._custom_endtime

    @property
    def default_payment_method(self):
        return self._default_payment_method

    @property
    def ref_plan_code(self):
        return self._ref_plan_code

    @property
    def number_members(self):
        return self._number_members

    @property
    def personal_trial_applied(self):
        return self._personal_trial_applied

    @property
    def enterprise_trial_applied(self):
        return self._enterprise_trial_applied

    @property
    def personal_trial_mobile_applied(self):
        return self._personal_trial_mobile_applied

    @property
    def personal_trial_web_applied(self):
        return self._personal_trial_web_applied

    @property
    def pm_stripe_subscription(self):
        return self._pm_stripe_subscription

    @property
    def pm_stripe_subscription_created_time(self):
        return self._pm_stripe_subscription_created_time

    @property
    def pm_mobile_subscription(self):
        return self._pm_mobile_subscription

    @property
    def extra_time(self):
        return self._extra_time

    @property
    def extra_plan(self):
        return self._extra_plan

    @property
    def attempts(self):
        return self._attempts

    @property
    def pm_plan(self):
        return self._pm_plan

    @property
    def promo_code(self):
        return self._promo_code

    def is_personal_trial_applied(self) -> bool:
        return self.personal_trial_applied

    def get_stripe_subscription(self):
        if not self.pm_stripe_subscription:
            return None
        return stripe.Subscription.retrieve(self.pm_stripe_subscription)
