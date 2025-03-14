import os
from typing import Optional, List, Union

from locker_server.shared.constants.attachments import UPLOAD_ACTION_ATTACHMENT


class AttachmentStorageService:
    def __init__(self, access_key: str = None, secret_key: str = None, endpoint_url: str = None, region: str = None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint_url = endpoint_url
        self.region = region

    @staticmethod
    def gen_action_key_path(action: str, attachment_id: str = None, **metadata) -> str:
        user_key = metadata.get("user_key")
        cipher_id = metadata.get("cipher_id")
        attachment_id = attachment_id or metadata.get("attachment_id")

        if action == UPLOAD_ACTION_ATTACHMENT:
            path = f"attachments/{user_key}/{cipher_id}/{attachment_id}"
        else:
            path = ""
        return path

    @classmethod
    def get_file_name(cls, file_path: str) -> tuple:
        """
        Get file name from file path
        :param file_path: (str)
        :return: (tuple) file name, extension
        """
        base = os.path.basename(file_path)
        file_name, extension = os.path.splitext(base)
        return file_name, extension.split("?")[0]

    @classmethod
    def validate_url(cls, attachment_url: str) -> Union[str, bool]:
        raise NotImplementedError

    @classmethod
    def get_file_path(cls, attachment_url: str) -> str:
        raise NotImplementedError

    def check_file_exist(self, file_path: str, source: str = None) -> bool:
        raise NotImplementedError

    def get_file_size(self, file_path: str, source: str = None) -> Optional[float]:
        raise NotImplementedError

    def get_folder_size(self, folder_path: str, source: str = None) -> Optional[float]:
        pass

    def generate_upload_form(self, upload_file_path: str, destination: str = None, **metadata):
        raise NotImplementedError

    def copy_file(self, old_file_path: str, new_file_path: str,
                  source: str = None, destination: str = None, **metadata) -> str:
        raise NotImplementedError

    def delete_files(self, file_paths: List[str], source: str = None) -> bool:
        raise NotImplementedError

    def delete_prefix(self, prefix: str, source: str = None) -> bool:
        raise NotImplementedError

    def list_files(self, prefix: str, source: str = None, max_keys: int = 1000, marker: str = '',
                   filter_type: str = None) -> tuple:
        raise NotImplementedError

    def generate_onetime_url(self, file_path: str, is_cdn=False, source: str = None, **kwargs) -> str:
        pass

    def upload_bytes_object(self, key: str, io_bytes, acl: str = "private", bucket: str = None, tagging=None):
        pass

    def get_object_content(self, object_key: str, bucket: str = None):
        pass
