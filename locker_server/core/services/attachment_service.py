import secrets
from typing import List, Dict

from locker_server.core.exceptions.cipher_attachment_exception import CipherAttachmentLimitSizeReachedException
from locker_server.shared.caching.attachment_upload_cache import get_reserved_upload_size, reserve_upload
from locker_server.shared.external_services.attachments.attachment import AttachmentStorageService
from locker_server.shared.constants.attachments import UPLOAD_ACTION_ATTACHMENT, LIMIT_SIZE_ATTACHMENT, \
    LIMIT_TOTAL_SIZE_ATTACHMENT, UPLOAD_FORM_EXPIRED


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
        user_key = metadata.get("user_key")
        if limit:
            if action in [UPLOAD_ACTION_ATTACHMENT]:
                current_folder_size = self.attachment_storage.get_folder_size(folder_path=f"attachments/{user_key}")
                # The upload forms which are not expired yet are counted, so the quota can not be exceeded by
                # requesting many upload forms at the same time
                reserved_size = get_reserved_upload_size(user_key=user_key)
                remain_size = max(LIMIT_TOTAL_SIZE_ATTACHMENT - (current_folder_size or 0) - reserved_size, 0)
                if remain_size <= 0:
                    raise CipherAttachmentLimitSizeReachedException
                limit_size = min(remain_size, LIMIT_SIZE_ATTACHMENT)
        upload_file_path = self.attachment_storage.gen_action_key_path(
            action=action, attachment_id=attachment_id, **metadata
        )
        upload_form = self.attachment_storage.generate_upload_form(
            upload_file_path=upload_file_path,
            **{
                "acl": acl, "limit": limit_size, "content_type": content_type, "method": metadata.get("method"),
                "expires_in": UPLOAD_FORM_EXPIRED
            }
        )
        if limit_size:
            reserve_upload(
                user_key=user_key, upload_key=upload_file_path, size=limit_size, expires_in=UPLOAD_FORM_EXPIRED
            )

        allocated_attachment = {
            "upload_id": upload_file_path,
            "limit_size": limit_size,
            "upload_form": upload_form,
        }
        return allocated_attachment

    def get_onetime_url(self, path: str, action: str = UPLOAD_ACTION_ATTACHMENT, is_cdn: bool = False, **kwargs):
        onetime_url = self.attachment_storage.generate_onetime_url(
            file_path=path, is_cdn=is_cdn, **kwargs
        )
        return onetime_url

    def delete_multiple_attachments(self, paths: List[str]):
        self.attachment_storage.delete_files(file_paths=paths)

    def delete_oversize_attachments(self, max_size: int = LIMIT_SIZE_ATTACHMENT, modified_after: float = None,
                                    execute: bool = True) -> Dict:
        """
        Delete the attachment files which are larger than the limit size.
        The presigned PUT urls do not limit the file size, so the oversize files are deleted after uploading
        :param max_size: (int) The max file size (bytes)
        :param modified_after: (float) Only check the files which are modified after this timestamp
        :param execute: (bool) Delete the oversize files or only report them (dry-run)
        :return: (dict) The statistic and the oversize keys
        """
        result = {"scanned": 0, "oversize": 0, "oversize_size": 0, "keys": [], "sizes": {}}
        for key, size, last_modified in self.attachment_storage.iter_keys(prefix="attachments/"):
            result["scanned"] += 1
            if not size or size <= max_size:
                continue
            if modified_after is not None and last_modified < modified_after:
                continue
            result["oversize"] += 1
            result["oversize_size"] += size
            result["keys"].append(key)
            result["sizes"][key] = size
        if execute and result["keys"]:
            self.attachment_storage.delete_files(file_paths=result["keys"])
        return result
