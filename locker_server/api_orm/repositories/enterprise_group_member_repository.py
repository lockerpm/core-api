from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_enterprise_group_member_model
from locker_server.core.entities.enterprise.group.group import EnterpriseGroup
from locker_server.core.entities.enterprise.group.group_member import EnterpriseGroupMember
from locker_server.core.repositories.enterprise_group_member_repository import EnterpriseGroupMemberRepository


EnterpriseGroupMemberORM = get_enterprise_group_member_model()
ModelParser = get_model_parser()


class EnterpriseGroupMemberORMRepository(EnterpriseGroupMemberRepository):
    # ------------------------ List EnterpriseGroupMember resource ------------------- #
    def list_by_group_id(self, enterprise_group_id: str) -> List[EnterpriseGroupMember]:
        group_members_orm = EnterpriseGroupMemberORM.objects.filter(
            group_id=enterprise_group_id
        ).select_related('group').select_related('member')
        return [ModelParser.enterprise_parser().parse_enterprise_group_member(
            enterprise_group_member_orm=group_member_orm
        ) for group_member_orm in group_members_orm]

    def list_group_member_user_email(self, enterprise_group_id: str) -> List:
        members = EnterpriseGroupMemberORM.objects.filter(
            group_id=enterprise_group_id
        ).values('member__user_id', 'member__email')
        return [{"user_id": m.get("member__user_id"), "email": m.get("member__email")} for m in members]

    # ------------------------ Get EnterpriseGroupMember resource --------------------- #

    # ------------------------ Create EnterpriseGroupMember resource --------------------- #

    # ------------------------ Update EnterpriseGroupMember resource --------------------- #

    # ------------------------ Delete EnterpriseGroupMember resource --------------------- #

