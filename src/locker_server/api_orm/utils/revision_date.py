from django.db.models import Q

from locker_server.api_orm.models import UserORM, TeamORM
from locker_server.shared.constants.members import PM_MEMBER_STATUS_CONFIRMED
from locker_server.shared.utils.app import now


def bump_account_revision_date(user: UserORM = None, team: TeamORM = None, **team_filters):
    if team:
        # Get all confirmed members
        team_members = team.team_members.filter(status=PM_MEMBER_STATUS_CONFIRMED)

        collection_ids = team_filters.get("collection_ids", [])
        role_name = team_filters.get("role_name", [])
        if collection_ids:
            team_members = team_members.filter(
                Q(role_id__in=role_name) | Q(collections_members__collection_id__in=collection_ids)
            )

        # Get list user ids and update revision date of them
        UserORM.objects.filter(user_id__in=team_members.values_list('user_id', flat=True)).update(
            revision_date=now()
        )
    elif user:
        user.revision_date = now()
        user.save()
