from django.db import models


class ScamSettingCategoryORM(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    name = models.CharField(max_length=512)
    name_vi = models.CharField(max_length=512)
    enabled = models.BooleanField(default=True)

    class Meta:
        db_table = 'cs_scam_setting_categories'
