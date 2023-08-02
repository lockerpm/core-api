from django.db import models

from locker_server.api_orm.abstracts.payments.promo_codes import AbstractPromoCodeORM
from locker_server.api_orm.models.payments.saas_market import SaasMarketORM
from locker_server.settings import locker_server_settings


class PromoCodeORM(AbstractPromoCodeORM):
    is_saas_code = models.BooleanField(default=False)
    saas_market = models.ForeignKey(SaasMarketORM, on_delete=models.SET_NULL, related_name="promo_codes", null=True)
    saas_plan = models.CharField(max_length=128, null=True, default=None)
    only_user = models.ForeignKey(
        locker_server_settings.LS_USER_MODEL, on_delete=models.CASCADE, related_name="only_promo_codes", null=True
    )
    only_period = models.CharField(max_length=128, null=True, default=None)

    class Meta(AbstractPromoCodeORM.Meta):
        swappable = 'LS_PROMO_CODE_MODEL'
        db_table = 'cs_promo_codes'

    @classmethod
    def create(cls, **data):
        pass

