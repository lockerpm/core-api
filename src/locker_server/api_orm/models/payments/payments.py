from django.db import models

from locker_server.api_orm.abstracts.payments.payments import AbstractPaymentORM
from locker_server.api_orm.models.payments.customers import CustomerORM


class PaymentORM(AbstractPaymentORM):
    customer = models.ForeignKey(CustomerORM, on_delete=models.SET_NULL, related_name="payments", null=True)

    class Meta:
        swappable = 'LS_PAYMENT_MODEL'
        db_table = 'cs_payments'

    @classmethod
    def create(cls, **data):
        pass
