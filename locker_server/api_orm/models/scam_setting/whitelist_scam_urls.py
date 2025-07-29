import uuid

from django.db import models

from locker_server.settings import locker_server_settings
from locker_server.shared.utils.app import now


class WhitelistScamUrlORM(models.Model):
    id = models.CharField(max_length=128, primary_key=True, default=uuid.uuid4)
    url = models.CharField(max_length=512)
    created_at = models.FloatField(default=now, null=True)
    updated_at = models.FloatField(default=None, null=True)

    user = models.ForeignKey(
        locker_server_settings.LS_USER_MODEL, on_delete=models.CASCADE, related_name="whitelist_urls"
    )

    class Meta:
        db_table = ("cs_whitelist_scam_urls")
        unique_together = ("user", "url")
