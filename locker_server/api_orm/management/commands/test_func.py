from django.core.management import BaseCommand

from locker_server.api_orm.models import *
from locker_server.api_orm.models.wrapper import *


class Command(BaseCommand):
    def handle(self, *args, **options):

        from locker_server.shared.constants.missions import USER_MISSION_STATUS_REWARD_SENT, USER_MISSION_STATUS_COMPLETED
        answer = "f0bs"
        is_claimed = UserRewardMissionORM.objects.filter(
            status__in=[USER_MISSION_STATUS_REWARD_SENT, USER_MISSION_STATUS_COMPLETED],
            answer=answer
        ).exists()
        print(is_claimed)
