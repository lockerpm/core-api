from abc import ABC, abstractmethod
from typing import List, Optional

from locker_server.core.entities.payment.country import Country


class CountryRepository(ABC):

    # ------------------------ List Country resource ------------------- #

    # ------------------------ Get Country resource --------------------- #
    @abstractmethod
    def get_country_by_code(self, country_id: str) -> Optional[Country]:
        pass

    @abstractmethod
    def get_country_by_name(self, country_name: str) -> Optional[Country]:
        pass
    # ------------------------ Create Country resource --------------------- #

    # ------------------------ Update Country resource --------------------- #

    # ------------------------ Delete Country resource --------------------- #
