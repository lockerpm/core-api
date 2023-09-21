from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.enterprise.group.group import EnterpriseGroup


class EnterpriseGroupRepository(ABC):
    # ------------------------ List EnterpriseGroup resource ------------------- #
    @abstractmethod
    def list_active_user_enterprise_group_ids(self, user_id: int) -> List[str]:
        pass

    # ------------------------ Get EnterpriseGroup resource --------------------- #
    @abstractmethod
    def get_by_id(self, enterprise_group_id: str) -> Optional[EnterpriseGroup]:
        pass

    # ------------------------ Create EnterpriseGroup resource --------------------- #

    # ------------------------ Update EnterpriseGroup resource --------------------- #
    @abstractmethod
    def add_group_member_to_share(self, enterprise_group_ids: List, new_member_ids: List):
        pass

    # ------------------------ Delete EnterpriseGroup resource --------------------- #

