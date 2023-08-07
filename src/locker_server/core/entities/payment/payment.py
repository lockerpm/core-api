from locker_server.core.entities.payment.customer import Customer
from locker_server.core.entities.payment.promo_code import PromoCode
from locker_server.core.entities.user.user import User
from locker_server.shared.constants.transactions import CURRENCY_USD, TRANSACTION_TYPE_PAYMENT, DURATION_MONTHLY


class Payment(object):
    def __init__(self, id: int, payment_id: str, created_time: float = None, total_price: float = 0,
                 discount: float = 0, currency: str = CURRENCY_USD, status: str = None, description: str = "",
                 transaction_type: str = TRANSACTION_TYPE_PAYMENT, payment_method: str = None,
                 failure_reason: str = None, stripe_invoice_id: str = None, mobile_invoice_id: str = None,
                 code: str = None, bank_id: int = None, scope: str = None, plan: str = None,
                 duration: str = DURATION_MONTHLY, metadata: str = None, enterprise_id: str = None, user: User = None,
                 promo_code: PromoCode = None, customer: Customer = None):
        self._id = id
        self._payment_id = payment_id
        self._created_time = created_time
        self._total_price = total_price
        self._discount = discount
        self._currency = currency
        self._status = status
        self._description = description
        self._transaction_type = transaction_type
        self._payment_method = payment_method
        self._failure_reason = failure_reason
        self._stripe_invoice_id = stripe_invoice_id
        self._mobile_invoice_id = mobile_invoice_id
        self._code = code
        self._bank_id = bank_id
        self._scope = scope
        self._plan = plan
        self._duration = duration
        self._metadata = metadata
        self._plan = plan
        self._enterprise_id = enterprise_id
        self._user = user
        self._promo_code = promo_code
        self._customer = customer

    @property
    def id(self):
        return self._id

    @property
    def payment_id(self):
        return self._payment_id

    @property
    def created_time(self):
        return self._created_time

    @property
    def total_price(self):
        return self._total_price

    @property
    def discount(self):
        return self._discount

    @property
    def currency(self):
        return self._currency

    @property
    def status(self):
        return self._status

    @property
    def description(self):
        return self._description

    @property
    def transaction_type(self):
        return self._transaction_type

    @property
    def payment_method(self):
        return self._payment_method

    @property
    def failure_reason(self):
        return self._failure_reason

    @property
    def stripe_invoice_id(self):
        return self._stripe_invoice_id

    @property
    def mobile_invoice_id(self):
        return self._mobile_invoice_id

    @property
    def code(self):
        return self._code

    @property
    def bank_id(self):
        return self._bank_id

    @property
    def scope(self):
        return self._scope

    @property
    def plan(self):
        return self._plan

    @property
    def duration(self):
        return self._duration

    @property
    def metadata(self):
        return self._metadata

    @property
    def enterprise_id(self):
        return self._enterprise_id

    @property
    def user(self):
        return self._user

    @property
    def promo_code(self):
        return self._promo_code

    @property
    def customer(self):
        return self._customer
