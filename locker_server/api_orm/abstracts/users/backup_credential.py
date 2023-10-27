from django.db import models

from locker_server.settings import locker_server_settings


class AbstractBackupCredentialORM(models.Model):
    master_password = models.CharField(max_length=300, null=True)
    master_password_hint = models.CharField(max_length=128, blank=True, null=True, default="")
    key = models.TextField(null=True)
    public_key = models.TextField(null=True)
    private_key = models.TextField(null=True)
    creation_date = models.FloatField()

    # Passwordless config
    fd_credential_id = models.CharField(max_length=255, null=True)
    fd_random = models.CharField(max_length=128, null=True)

    user = models.ForeignKey(locker_server_settings.LS_USER_MODEL, on_delete=models.CASCADE,
                             related_name="user_backup_credentials")

    class Meta:
        abstract = True

    @classmethod
    def create(cls, device, **data):
        raise NotImplementedError
