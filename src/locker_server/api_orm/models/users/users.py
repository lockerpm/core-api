from django.contrib.auth import password_validation
from django.db import models

from locker_server.api_orm.abstracts.users.users import AbstractUserORM
from locker_server.shared.constants.lang import LANG_ENGLISH
from locker_server.shared.utils.app import now


class UserORM(AbstractUserORM):
    email = models.EmailField(unique=True, max_length=255)
    full_name = models.CharField(max_length=255)
    language = models.CharField(max_length=4, blank=False, default=LANG_ENGLISH)
    # FA2
    is_factor2 = models.BooleanField(default=False)
    base32_secret_factor2 = models.CharField(max_length=16, blank=True, default="")

    class Meta(AbstractUserORM.Meta):
        swappable = 'LS_USER_MODEL'
        db_table = 'cs_users'

    @classmethod
    def retrieve_or_create(cls, **kwargs):
        email = kwargs.get("email")
        full_name = kwargs.get("full_name") or email
        creation_date = kwargs.get("creation_date") or now()
        creation_date = now() if not creation_date else creation_date
        user, is_created = cls.objects.get_or_create(email=email, defaults={
            "email": email, "full_name": full_name, "creation_date": creation_date,
        })
        if is_created is True:
            PMUserPlan.update_or_create(user)
            return user
        return user

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None
