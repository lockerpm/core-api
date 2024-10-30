from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.extension.autofill_key import AutofillKey


class AutofillKeyRepository(ABC):
    # ------------------------ List AutofillKey resource ------------------- #
    @abstractmethod
    def list_autofill_keys(self, **filters) -> List[AutofillKey]:
        pass

    # ------------------------ Get AutofillKey resource --------------------- #
    @abstractmethod
    def get_autofill_key(self, key: str) -> Optional[AutofillKey]:
        pass

    # ------------------------ Create AutofillKey resource --------------------- #
    @abstractmethod
    def create_autofill_key(self, **create_data) -> AutofillKey:
        pass

    # ------------------------ Update AutofillKey resource --------------------- #
    @abstractmethod
    def update_autofill_key(self, key: str, **update_data) -> AutofillKey:
        pass

    # ------------------------ Delete AutofillKey resource --------------------- #
    @abstractmethod
    def delete_autofill_key(self, key: str) -> bool:
        pass
