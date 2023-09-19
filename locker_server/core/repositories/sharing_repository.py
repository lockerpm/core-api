from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.member.team_member import TeamMember
from locker_server.core.entities.team.team import Team


class SharingRepository(ABC):
    # ------------------------ List Sharing resource ------------------- #
    @abstractmethod
    def list_sharing_invitations(self, user_id: int, personal_share: bool = True) -> List[TeamMember]:
        pass

    # ------------------------ Get Sharing resource --------------------- #
    @abstractmethod
    def get_shared_members(self, personal_shared_team: Team,
                           exclude_owner=True, is_added_by_group=None) -> List[TeamMember]:
        pass

    @abstractmethod
    def get_sharing_cipher_type(self, sharing_id: str) -> Union[str, int]:
        pass

    # ------------------------ Create Sharing resource --------------------- #

    # ------------------------ Update Sharing resource --------------------- #

    # ------------------------ Delete Sharing resource --------------------- #

