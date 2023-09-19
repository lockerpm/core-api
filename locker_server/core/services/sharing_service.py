from typing import List, Optional, Dict, Union

from locker_server.core.entities.cipher.cipher import Cipher
from locker_server.core.entities.member.member_role import MemberRole
from locker_server.core.entities.member.team_member import TeamMember
from locker_server.core.entities.team.team import Team
from locker_server.core.entities.user.user import User
from locker_server.core.exceptions.cipher_exception import FolderDoesNotExistException, CipherMaximumReachedException, \
    CipherDoesNotExistException
from locker_server.core.exceptions.collection_exception import CollectionDoesNotExistException, \
    CollectionCannotRemoveException, CollectionCannotAddException
from locker_server.core.exceptions.team_exception import TeamDoesNotExistException, TeamLockedException
from locker_server.core.exceptions.team_member_exception import OnlyAllowOwnerUpdateException, \
    TeamMemberDoesNotExistException, OwnerDoesNotExistException
from locker_server.core.repositories.cipher_repository import CipherRepository
from locker_server.core.repositories.sharing_repository import SharingRepository
from locker_server.core.repositories.team_member_repository import TeamMemberRepository
from locker_server.core.repositories.team_repository import TeamRepository
from locker_server.core.repositories.user_plan_repository import UserPlanRepository
from locker_server.shared.constants.members import *
from locker_server.shared.utils.app import diff_list


class SharingService:
    """
    This class represents Use Cases related Sharing
    """
    def __init__(self, sharing_repository: SharingRepository,
                 team_repository: TeamRepository,
                 team_member_repository: TeamMemberRepository):
        self.sharing_repository = sharing_repository
        self.team_repository = team_repository
        self.team_member_repository = team_member_repository

    @staticmethod
    def get_personal_share_type(member: TeamMember = None, role: str = None):
        if not role:
            role = member.role.name
        if role in [MEMBER_ROLE_MEMBER]:
            if member.hide_passwords is True:
                return MEMBER_SHARE_TYPE_ONLY_FILL
            else:
                return MEMBER_SHARE_TYPE_VIEW
        return MEMBER_SHARE_TYPE_EDIT

    def get_shared_members(self, personal_shared_team: Team,
                           exclude_owner=True, is_added_by_group=None) -> List[TeamMember]:
        return self.sharing_repository.get_shared_members(
            personal_shared_team=personal_shared_team, exclude_owner=exclude_owner, is_added_by_group=is_added_by_group
        )

    def get_by_id(self, sharing_id: str) -> Optional[Team]:
        sharing = self.team_repository.get_by_id(team_id=sharing_id)
        if not sharing:
            raise TeamDoesNotExistException
        return sharing

    def list_sharing_invitations(self, user_id: int, personal_share=True) -> List[TeamMember]:
        return self.sharing_repository.list_sharing_invitations(user_id=user_id, personal_share=personal_share)

    def get_sharing_owner(self, sharing_id: str) -> Optional[TeamMember]:
        owner = self.team_member_repository.get_primary_member(team_id=sharing_id)
        if not owner:
            raise OwnerDoesNotExistException
        return owner

    def is_folder_sharing(self, sharing_id: str) -> bool:
        return True if self.team_repository.list_team_collection_ids(team_id=sharing_id) else False

    def get_sharing_cipher_type(self, sharing_id: str) -> Union[str, int]:
        return self.sharing_repository.get_sharing_cipher_type(sharing_id=sharing_id)
