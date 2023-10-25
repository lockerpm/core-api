import uuid

from django.conf import settings
from django.db import models

from locker_server.settings import locker_server_settings


class AbstractEnterpriseAvatarORM(models.Model):
    id = models.CharField(primary_key=True, max_length=128, default=uuid.uuid4)
    avatar = models.ImageField(null=True, default=None, upload_to=settings.ENTERPRISE_AVATAR_URL)

    enterprise = models.OneToOneField(
        locker_server_settings.LS_ENTERPRISE_MODEL, on_delete=models.CASCADE,
        related_name="enterprise_avatar"
    )

    class Meta:
        abstract = True

    @classmethod
    def create(cls, **data):
        raise NotImplementedError
