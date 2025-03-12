import secrets
from typing import Optional

# from locker_server.core.entities.cipher.cipher_attachment import CipherAttachment
# from locker_server.core.exceptions.cipher_attachment_repository import CipherAttachmentDoesNotExistException
# from locker_server.core.repositories.cipher_attachment_repository import CipherAttachmentRepository
from locker_server.shared.external_services.attachments.attachment import AttachmentStorageService
from locker_server.shared.constants.attachments import UPLOAD_ACTION_ATTACHMENT, LIMIT_SIZE_ATTACHMENT


class AttachmentService:
    """
    This class represents Use Cases related attachments
    """

    def __init__(self,
                 attachment_storage: AttachmentStorageService):
        # self.cipher_attachment_repository = cipher_attachment_repository
        self.attachment_storage = attachment_storage

    @staticmethod
    def generate_attachment_id() -> str:
        attachment_id = secrets.randbits(64)
        return str(attachment_id)

    # def get_cipher_attachment_by_path(self, path: str) -> Optional[CipherAttachment]:
    #     cipher_attachment = self.cipher_attachment_repository.get_by_path(path=path)
    #     if not cipher_attachment:
    #         raise CipherAttachmentDoesNotExistException
    #     return cipher_attachment

    def get_attachment_upload_form(self, action: str, file_name: str = None, **metadata):
        acl = "private"
        limit = metadata.get("limit", True)
        limit_size = None
        content_type = None
        attachment_id = self.generate_attachment_id()
        if limit:
            if action in [UPLOAD_ACTION_ATTACHMENT]:
                limit_size = LIMIT_SIZE_ATTACHMENT
        upload_file_path = self.attachment_storage.gen_action_key_path(
            action=action, attachment_id=attachment_id, **metadata
        )
        upload_form = self.attachment_storage.generate_upload_form(
            upload_file_path=upload_file_path,
            **{"acl": acl, "limit": limit_size, "content_type": content_type}
        )

        allocated_attachment = {
            "upload_id": upload_file_path,
            "upload_form": upload_form,
        }
        return allocated_attachment

    def get_onetime_url(self, path: str, action: str = UPLOAD_ACTION_ATTACHMENT, is_cdn: bool = False, **kwargs):
        onetime_url = self.attachment_storage.generate_onetime_url(
            file_path=path, is_cdn=is_cdn, **kwargs
        )
        return onetime_url
