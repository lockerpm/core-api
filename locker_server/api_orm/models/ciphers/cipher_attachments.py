from django.db import models

from locker_server.settings import locker_server_settings


class CipherAttachmentORM(models.Model):
    id = models.BigAutoField(primary_key=True)
    creation_date = models.FloatField()
    path = models.CharField(max_length=255, unique=True)
    file_name = models.CharField(max_length=128)
    size = models.IntegerField(null=True)
    key = models.TextField(null=True)
    cipher = models.ForeignKey(
        locker_server_settings.LS_CIPHER_MODEL, on_delete=models.CASCADE, related_name="cipher_attachments"
    )

    class Meta:
        db_table = 'cs_cipher_attachments'
