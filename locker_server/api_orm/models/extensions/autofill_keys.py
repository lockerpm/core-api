from django.db import models

from locker_server.settings import locker_server_settings
from locker_server.shared.utils.app import now


class AutofillKeyORM(models.Model):
    key = models.CharField(max_length=255, unique=True)
    values = models.TextField(null=True, blank=True)
    created_time = models.FloatField(default=now, null=True)
    updated_time = models.FloatField(null=True)

    class Meta:
        db_table = 'extension_autofill_keys'
