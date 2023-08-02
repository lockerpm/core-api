from django.db import models

from locker_server.settings import locker_server_settings


class PMUserPlanFamily(models.Model):
    created_time = models.IntegerField()
    email = models.CharField(max_length=128, null=True)
    user = models.ForeignKey(
        locker_server_settings.LS_USER_MODEL, on_delete=models.CASCADE, related_name="pm_plan_family", null=True
    )
    root_user_plan = models.ForeignKey(
        PMUserPlan, on_delete=models.CASCADE, related_name="pm_plan_family"
    )

    class Meta:
        abstract = True

    @classmethod
    def create(cls, root_user_plan, user, email):
        raise NotImplementedError

    @classmethod
    def create_multiple_by_email(cls, root_user_plan, *emails):
        raise NotImplementedError
