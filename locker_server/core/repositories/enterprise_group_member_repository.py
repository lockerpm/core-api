from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.enterprise.group.group import EnterpriseGroup
from locker_server.core.entities.enterprise.group.group_member import EnterpriseGroupMember


class EnterpriseGroupMemberRepository(ABC):
    # ------------------------ List EnterpriseGroupMember resource ------------------- #
    @abstractmethod
    def list_by_group_id(self, enterprise_group_id: str) -> List[EnterpriseGroupMember]:
        pass

    @abstractmethod
    def list_group_member_user_email(self, enterprise_group_id: str) -> List:
        pass

    # ------------------------ Get EnterpriseGroupMember resource --------------------- #

    # ------------------------ Create EnterpriseGroupMember resource --------------------- #

    # ------------------------ Update EnterpriseGroupMember resource --------------------- #

    # ------------------------ Delete EnterpriseGroupMember resource --------------------- #

