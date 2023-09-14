from typing import List, Optional, Dict

from locker_server.core.entities.cipher.cipher import Cipher
from locker_server.core.entities.member.team_member import TeamMember
from locker_server.core.entities.team.team import Team
from locker_server.core.entities.user.user import User
from locker_server.core.exceptions.cipher_exception import FolderDoesNotExistException, CipherMaximumReachedException, \
    CipherDoesNotExistException
from locker_server.core.exceptions.collection_exception import CollectionDoesNotExistException, \
    CollectionCannotRemoveException, CollectionCannotAddException
from locker_server.core.exceptions.team_exception import TeamDoesNotExistException, TeamLockedException
from locker_server.core.exceptions.team_member_exception import OnlyAllowOwnerUpdateException
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
    def __init__(self, sharing_repository: SharingRepository):
        self.sharing_repository = sharing_repository

    @staticmethod
    def get_personal_share_type(member: TeamMember):
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
