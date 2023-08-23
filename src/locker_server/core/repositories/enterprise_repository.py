from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.enterprise.enterprise import Enterprise
from locker_server.core.entities.user.user import User


class EnterpriseRepository(ABC):
    # ------------------------ List Enterprise resource ------------------- #
    @abstractmethod
    def list_user_enterprises(self, user_id: int, **filter_params) -> List[Enterprise]:
        pass

    # ------------------------ Get Enterprise resource --------------------- #

    # ------------------------ Create Enterprise resource --------------------- #

    # ------------------------ Update Enterprise resource --------------------- #

    # ------------------------ Delete EnterpriseMember resource --------------------- #
    @abstractmethod
    def delete_completely(self, enterprise: Enterprise):
        pass

    @abstractmethod
    def clear_data(self, enterprise: Enterprise):
        pass
