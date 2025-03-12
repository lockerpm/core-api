from typing import Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.cipher.cipher_attachment import CipherAttachment


class CipherAttachmentRepository(ABC):
    # ------------------------ List Attachment resource ------------------- #

    # ------------------------ Get Attachment resource --------------------- #
    @abstractmethod
    def get_by_id(self, attachment_id: int):
        pass

    @abstractmethod
    def get_by_path(self, path: str, parse_cipher: bool = False) -> Optional[CipherAttachment]:
        pass

    # ------------------------ Create Attachment resource --------------------- #

    # ------------------------ Update Attachment resource --------------------- #


    # ------------------------ Delete Attachment resource --------------------- #
