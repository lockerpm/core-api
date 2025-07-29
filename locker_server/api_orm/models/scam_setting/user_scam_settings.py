from django.db import models

from locker_server.api_orm.models.scam_setting.scam_setting_category import ScamSettingCategoryORM
from locker_server.settings import locker_server_settings
from locker_server.shared.utils.app import now


class ScamSettingORM(models.Model):
    enabled = models.BooleanField(default=True)
    created_at = models.FloatField(default=now, null=True)
    updated_at = models.FloatField(default=None, null=True)

    user = models.ForeignKey(
        locker_server_settings.LS_USER_MODEL, on_delete=models.CASCADE, related_name="scam_settings"
    )
    category = models.ForeignKey(
        ScamSettingCategoryORM, on_delete=models.CASCADE,
        related_name="scam_settings"
    )

    class Meta:
        db_table = 'cs_user_scam_settings'
        unique_together = ('user', 'category')
