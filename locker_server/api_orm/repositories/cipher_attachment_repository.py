from typing import Optional

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models import CipherAttachmentORM
from locker_server.core.entities.cipher.cipher_attachment import CipherAttachment
from locker_server.core.repositories.cipher_attachment_repository import CipherAttachmentRepository


ModelParser = get_model_parser()


class CipherAttachmentORMRepository(CipherAttachmentRepository):
    # ------------------------ List Attachment resource ------------------- #

    # ------------------------ Get Attachment resource --------------------- #
    def get_by_id(self, attachment_id: int):
        pass

    def get_by_path(self, path: str, parse_cipher: bool = False) -> Optional[CipherAttachment]:
        try:
            cipher_attachment_orm = CipherAttachmentORM.objects.get(path=path)
        except CipherAttachmentORM.DoesNotExist:
            return None
        return ModelParser.cipher_parser().parse_cipher_attachment(
            cipher_attachment_orm=cipher_attachment_orm, parse_cipher=parse_cipher
        )

    # ------------------------ Create Attachment resource --------------------- #

    # ------------------------ Update Attachment resource --------------------- #

    # ------------------------ Delete Attachment resource --------------------- #
