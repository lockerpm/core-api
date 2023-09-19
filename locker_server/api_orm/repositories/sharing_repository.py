from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from django.db.models import When, Q, IntegerField, Value, Case

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_team_model, get_team_member_model, get_cipher_model
from locker_server.core.entities.member.team_member import TeamMember
from locker_server.core.entities.team.team import Team
from locker_server.core.repositories.sharing_repository import SharingRepository
from locker_server.shared.constants.members import *


TeamORM = get_team_model()
TeamMemberORM = get_team_member_model()
CipherORM = get_cipher_model()
ModelParser = get_model_parser()


class SharingORMRepository(SharingRepository):
    # ------------------------ List Sharing resource ------------------- #
    def list_sharing_invitations(self, user_id: int, personal_share: bool = True) -> List[TeamMember]:
        member_invitations_orm = TeamMemberORM.objects.filter(
            user_id=user_id, status__in=[PM_MEMBER_STATUS_INVITED, PM_MEMBER_STATUS_ACCEPTED],
            team__personal_share=personal_share,
        ).select_related('team').order_by('access_time')
        return [ModelParser.team_parser().parse_team_member(team_member_orm=m) for m in member_invitations_orm]

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

    def get_sharing_cipher_type(self, sharing_id: str) -> Union[str, int]:
        share_cipher_orm = CipherORM.objects.get(team_id=sharing_id).first()
        return share_cipher_orm.type if share_cipher_orm else None

    # ------------------------ Create Sharing resource --------------------- #

    # ------------------------ Update Sharing resource --------------------- #

    # ------------------------ Delete Sharing resource --------------------- #

