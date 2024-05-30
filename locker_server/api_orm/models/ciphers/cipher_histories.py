import ast
import uuid

from django.db import models

from locker_server.settings import locker_server_settings
from locker_server.shared.utils.app import now


class CipherHistoryORM(models.Model):
    id = models.CharField(primary_key=True, max_length=128, default=uuid.uuid4)
    creation_date = models.FloatField()
    revision_date = models.FloatField()
    last_use_date = models.FloatField(null=True)
    reprompt = models.IntegerField(default=0)
    score = models.FloatField(default=0)
    data = models.TextField(blank=True, null=True)
    cipher = models.ForeignKey(
        locker_server_settings.LS_CIPHER_MODEL, on_delete=models.CASCADE, related_name="cipher_histories"
    )

    class Meta:
        db_table = 'cs_cipher_histories'

    @classmethod
    def create(cls, cipher, **data):
        cipher_history_orm = cls(
            creation_date=data.get("creation_date", now()),
            revision_date=data.get("revision_date", now()),
            last_use_date=data.get("last_use_date"),
            reprompt=data.get("reprompt", 0),
            score=data.get("score", 0),
            data=data.get("data"),
            cipher=cipher
        )
        cipher_history_orm.save()
        return cipher_history_orm

    def get_data(self):
        if not self.data:
            return {}
        return ast.literal_eval(str(self.data))