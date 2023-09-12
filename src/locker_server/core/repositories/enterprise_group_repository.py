from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod


class EnterpriseGroupRepository(ABC):
    # ------------------------ List EnterpriseGroup resource ------------------- #

    # ------------------------ Get EnterpriseGroup resource --------------------- #

    # ------------------------ Create EnterpriseGroup resource --------------------- #

    # ------------------------ Update EnterpriseGroup resource --------------------- #
    @abstractmethod
    def add_group_member_to_share(self, enterprise_group_ids: List, new_member_ids: List):
        pass

    # ------------------------ Delete EnterpriseGroup resource --------------------- #

