from django.db import models

from locker_server.api_orm.abstracts.payments.promo_codes import AbstractPromoCodeORM
from locker_server.api_orm.models.payments.saas_market import SaasMarketORM
from locker_server.settings import locker_server_settings
from locker_server.shared.constants.transactions import PLAN_TYPE_PM_LIFETIME
from locker_server.shared.utils.app import now

PromoCodeTypeORM = locker_server_settings.LS_PROMO_CODE_TYPE_MODEL


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
        expired_time = data.get("expired_time")
        if not expired_time:
            expired_time = now() + data.get("day_expired") * 86400

        number_code = data['number_code']
        promo_type = data['type']
        code = data['code']
        value = data['value']
        limit_value = data.get("limit_value")
        currency = data.get("currency", "USD")
        duration = data.get("duration", 1)
        specific_duration = data.get("specific_duration")
        description_en = data.get("description_en", "")
        description_vi = data.get("description_vi", "")
        only_user_id = data.get("only_user_id")
        only_period = data.get("only_period")
        only_plan = data.get("only_plan")
        is_saas_code = data.get("is_saas_code", False)
        saas_market_id = data.get("saas_market_id", None)
        saas_plan = data.get("saas_plan")
        if is_saas_code is True:
            saas_plan = saas_plan or PLAN_TYPE_PM_LIFETIME

        new_promo_code = cls(
            created_time=now(), expired_time=expired_time, remaining_times=number_code, code=code,
            value=value, limit_value=limit_value, currency=currency,
            type=PromoCodeTypeORM.objects.get(name=promo_type),
            duration=duration, specific_duration=specific_duration,
            description_vi=description_vi, description_en=description_en,
            only_user_id=only_user_id,
            only_period=only_period,
            only_plan=only_plan,
            is_saas_code=is_saas_code, saas_market_id=saas_market_id, saas_plan=saas_plan
        )
        new_promo_code.save()
        return new_promo_code
