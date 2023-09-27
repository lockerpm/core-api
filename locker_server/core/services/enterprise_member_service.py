from typing import Optional, List

from locker_server.core.entities.enterprise.member.enterprise_member import EnterpriseMember
from locker_server.core.exceptions.enterprise_member_exception import EnterpriseMemberDoesNotExistException
from locker_server.core.repositories.enterprise_group_member_repository import EnterpriseGroupMemberRepository
from locker_server.core.repositories.enterprise_member_repository import EnterpriseMemberRepository
from locker_server.core.repositories.enterprise_repository import EnterpriseRepository


class EnterpriseMemberService:
    """
    This class represents Use Cases related Enterprise Member
    """

    def __init__(self, enterprise_repository: EnterpriseRepository,
                 enterprise_member_repository: EnterpriseMemberRepository,
                 enterprise_group_member_repository: EnterpriseGroupMemberRepository
                 ):
        self.enterprise_repository = enterprise_repository
        self.enterprise_member_repository = enterprise_member_repository
        self.enterprise_group_member_repository = enterprise_group_member_repository

    def list_enterprise_members(self, **filters) -> List[EnterpriseMember]:
        return self.enterprise_member_repository.list_enterprise_members(**filters)

    def list_enterprise_member_user_id_by_roles(self, enterprise_id: str, role_ids: List[str]) -> List[str]:
        return self.enterprise_member_repository.list_enterprise_member_user_id_by_roles(
            enterprise_id=enterprise_id,
            role_ids=role_ids
        )

    def list_enterprise_member_user_id_by_members(self, enterprise_id: str, member_ids: List[str]) -> List[str]:
        return self.enterprise_member_repository.list_enterprise_member_user_id_by_members(
            enterprise_id=enterprise_id,
            member_ids=member_ids
        )

    def get_member_by_user(self, use_id: int, enterprise_id: str) -> Optional[EnterpriseMember]:
        enterprise_member = self.enterprise_member_repository.get_enterprise_member_by_user_id(
            user_id=use_id,
            enterprise_id=enterprise_id
        )
        if not enterprise_member:
            raise EnterpriseMemberDoesNotExistException
        return enterprise_member

    def list_enterprise_member_user_id_by_group_id(self, enterprise_id: str, group_id: str) -> List[str]:
        return self.enterprise_group_member_repository.list_enterprise_group_member_user_id_by_id(
            enterprise_id=enterprise_id,
            enterprise_group_id=group_id
        )
