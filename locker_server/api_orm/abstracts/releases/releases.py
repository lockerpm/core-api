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
    checksum = models.TextField(null=True, default=None)
    platform = models.CharField(max_length=32, db_index=True, null=True, default=None)
    stable = models.BooleanField(default=False)

    class Meta:
        abstract = True

    @classmethod
    def create(cls, **data):
        new_release = cls(
            created_time=now(),
            major=data.get("major"),
            minor=data.get("minor"),
            patch=data.get("patch", ""),
            build_number=data.get("build_number", ""),
            description_en=data.get("description_en", ""),
            client_id=data.get("client_id"),
            environment=data.get("environment", "prod"),
            checksum=data.get("checksum"),
            platform=data.get("platform"),
            stable=data.get("stable", False)
        )
        new_release.save()
        return new_release

    @property
    def version(self):
        ver = f"{self.major}.{self.minor}"
        if self.patch:
            ver += f".{self.patch}"
        if self.build_number:
            ver += f".{self.build_number}"
        return ver
