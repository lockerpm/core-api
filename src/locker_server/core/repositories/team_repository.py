from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.team.collection import Collection


class TeamRepository(ABC):
    # ------------------------ List Team resource ------------------- #
    @abstractmethod
    def list_team_collection_ids(self, team_id: str) -> List[str]:
        pass

    # ------------------------ Get Team resource --------------------- #
    @abstractmethod
    def get_default_collection(self, team_id: str) -> Optional[Collection]:
        pass

    # ------------------------ Create Team resource --------------------- #

    # ------------------------ Update Team resource --------------------- #

    # ------------------------ Delete Team resource --------------------- #

