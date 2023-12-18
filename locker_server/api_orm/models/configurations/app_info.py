from django.conf import settings
from django.db import models, transaction

from locker_server.shared.utils.app import now


def image_upload_path(instance, filename):
    return settings.MEDIA_ROOT + '/logo/{0}/{1}'.format(instance.id, filename)


class AppInfoORM(models.Model):
    logo = models.ImageField(null=True, default=None, upload_to=image_upload_path)
    name = models.CharField(null=True, default=None, max_length=255)
    creation_date = models.FloatField(null=True, default=None)
    revision_date = models.FloatField(null=True, default=None)

    class Meta:
        db_table = 'cs_app_info'

    @classmethod
    def create(cls, **data):
        with transaction.atomic():
            try:
                app_info_orm = cls.objects.get()
            except cls.DoesNotExist:
                app_info_orm = cls.objects.create(
                    name=data.get("name"),
                    creation_date=now()
                )
            return app_info_orm
