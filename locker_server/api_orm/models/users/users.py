import json
import requests

from django.conf import settings
from django.contrib.auth import password_validation
from django.db import models

from locker_server.api_orm.abstracts.users.users import AbstractUserORM
from locker_server.shared.constants.lang import LANG_ENGLISH
from locker_server.shared.external_services.requester.retry_requester import requester
from locker_server.shared.log.cylog import CyLog
from locker_server.shared.utils.app import now


class UserORM(AbstractUserORM):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=255, null=True)
    full_name = models.CharField(max_length=255, null=True)
    language = models.CharField(max_length=4, blank=False, default=LANG_ENGLISH)
    # FA2
    is_factor2 = models.BooleanField(default=False)
    base32_secret_factor2 = models.CharField(max_length=16, blank=True, default="")

    is_super_admin = models.BooleanField(default=False)
    sync_all_platforms = models.BooleanField(default=False)
    is_password_changed = models.BooleanField(default=False)

    class Meta(AbstractUserORM.Meta):
        swappable = 'LS_USER_MODEL'
        db_table = 'cs_users'

    @classmethod
    def retrieve_or_create(cls, **kwargs):
        email = kwargs.get("email")
        full_name = kwargs.get("full_name") or email
        is_super_admin = kwargs.get("is_super_admin", False)
        is_password_changed = kwargs.get("is_password_changed", False)
        creation_date = kwargs.get("creation_date") or now()
        creation_date = now() if not creation_date else creation_date
        user, is_created = cls.objects.get_or_create(email=email, defaults={
            "email": email, "full_name": full_name, "creation_date": creation_date,
            "is_super_admin": is_super_admin,
            "is_password_changed": is_password_changed
        })
        if is_created is True:
            from locker_server.api_orm.models.user_plans.pm_user_plan import PMUserPlanORM
            PMUserPlanORM.update_or_create(user)
            return user
        return user

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None

    @classmethod
    def get_infor_by_user_ids(cls, user_ids, **filter_params):
        url = f"{settings.GATEWAY_API}/micro_services/users"
        headers = {'Authorization': settings.MICRO_SERVICE_USER_AUTH}
        data_send = {"ids": user_ids, "emails": [], "q": filter_params.get("q")}
        data_send.update(filter_params)
        res = requester(method="POST", url=url, headers=headers, data_send=data_send, retry=True)
        if res.status_code == 200:
            return res.json()
        return []

    @classmethod
    def get_user_data_by_user_ids(cls, user_ids, **filter_params):
        users_data = cls.get_infor_by_user_ids(user_ids=list(set(user_ids)), **filter_params)
        users_data_dict = dict()
        for user_data in users_data:
            users_data_dict[user_data.get("id")] = user_data
        return users_data_dict

    def get_from_cystack_id(self):
        """
        Request to API Gateway to get user information
        :return:
        """
        url = "{}/micro_services/users/{}".format(settings.GATEWAY_API, self.user_id)
        headers = {'Authorization': settings.MICRO_SERVICE_USER_AUTH}
        try:
            res = requester(method="GET", url=url, headers=headers)
            if res.status_code == 200:
                try:
                    return res.json()
                except json.JSONDecodeError:
                    CyLog.error(**{"message": f"[!] User.get_from_cystack_id JSON Decode error: {res.url} {res.text}"})
                    return {}
            return {}
        except (requests.RequestException, requests.ConnectTimeout):
            return {}
