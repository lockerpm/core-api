from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from django.db.models import When, Q, IntegerField, Value, Case

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_team_model, get_team_member_model
from locker_server.core.entities.member.team_member import TeamMember
from locker_server.core.entities.team.team import Team
from locker_server.core.repositories.sharing_repository import SharingRepository
from locker_server.shared.constants.members import *


TeamORM = get_team_model()
TeamMemberORM = get_team_member_model()
ModelParser = get_model_parser()


class SharingORMRepository(SharingRepository):
    # ------------------------ List Sharing resource ------------------- #

    # ------------------------ Get Sharing resource --------------------- #
    def get_shared_members(self, personal_shared_team: Team,
                           exclude_owner=True, is_added_by_group=None) -> List[TeamMember]:
        order_whens = [
            When(Q(role__name=MEMBER_ROLE_OWNER, user__isnull=False), then=Value(2)),
            When(Q(role__name=MEMBER_ROLE_ADMIN, user__isnull=False), then=Value(3)),
            When(Q(role__name=MEMBER_ROLE_MEMBER, user__isnull=False), then=Value(4))
        ]
        members_orm = TeamMemberORM.objects.filter(team_id=personal_shared_team.team_id).annotate(
            order_field=Case(*order_whens, output_field=IntegerField(), default=Value(4))
        ).order_by("order_field").select_related('user').select_related('role').select_related('team')
        if exclude_owner:
            members_orm = members_orm.exclude(role_id=MEMBER_ROLE_OWNER)
        if is_added_by_group is not None:
            members_orm = members_orm.filter(is_added_by_group=is_added_by_group)

        return [ModelParser.team_parser().parse_team_member(team_member_orm=member_orm) for member_orm in members_orm]

    # ------------------------ Create Sharing resource --------------------- #

    # ------------------------ Update Sharing resource --------------------- #

    # ------------------------ Delete Sharing resource --------------------- #

