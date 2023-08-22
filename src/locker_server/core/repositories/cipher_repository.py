from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.cipher.cipher import Cipher
from locker_server.core.entities.cipher.folder import Folder
from locker_server.core.entities.user.device import Device
from locker_server.core.entities.user.user import User


class CipherRepository(ABC):
    # ------------------------ List Cipher resource ------------------- #
    @abstractmethod
    def list_cipher_collection_ids(self, cipher_id: str) -> List[str]:
        pass

    # ------------------------ Get Cipher resource --------------------- #

    @abstractmethod
    def get_user_folder(self, user_id: int, folder_id: str) -> Optional[Folder]:
        pass

    @abstractmethod
    def count_ciphers_created_by_user(self, user_id: int, **filter_params) -> int:
        pass

    @abstractmethod
    def get_master_pwd_item(self, user_id: int) -> Optional[Cipher]:
        pass

    # ------------------------ Create Cipher resource --------------------- #
    def create_cipher(self, cipher_data: Dict) -> Cipher:
        pass

    # ------------------------ Update Cipher resource --------------------- #
    def update_cipher(self, cipher_id: str, cipher_data: Dict) -> Cipher:
        pass

    # ------------------------ Delete Cipher resource --------------------- #
