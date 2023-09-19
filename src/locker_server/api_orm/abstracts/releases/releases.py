from django.db import models

from locker_server.shared.utils.app import now


class AbstractReleaseORM(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.IntegerField()
    major = models.CharField(max_length=16)
    minor = models.CharField(max_length=16)
    patch = models.CharField(max_length=16, blank=True, default="")
    build_number = models.CharField(max_length=16, blank=True, default="")
    description_en = models.CharField(max_length=512, blank=True, default="")
    description_vi = models.CharField(max_length=512, blank=True, default="")
    client_id = models.CharField(max_length=128)
    environment = models.CharField(max_length=128, default="prod")

    class Meta:
        abstract = True

    @classmethod
    def create(cls, **data):
        raise NotImplementedError


    @property
    def version(self):
        ver = f"{self.major}.{self.minor}"
        if self.patch:
            ver += f".{self.patch}"
        if self.build_number:
            ver += f".{self.build_number}"
        return ver
