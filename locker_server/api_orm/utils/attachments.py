import ast
import traceback
from typing import Iterable, List, Optional

from locker_server.settings import locker_server_settings
from locker_server.shared.background.i_background import BackgroundThread, background_exception_wrapper
from locker_server.shared.external_services.attachments.attachment_factory import AttachmentStorageFactory
from locker_server.shared.log.cylog import CyLog
from locker_server.shared.utils.app import md5_encode
from locker_server.shared.utils.attachments import ATTACHMENT_KEY_PATTERN, normalize_attachment_key


class AttachmentKeys:
    """
    The storage keys of the attachments that must be deleted
    - prefixes: attachments/{user_key}/{cipher_id}/ of the cipher creator/owner
    - keys: exact keys from the cipher data (e.g. uploaded by other team members)
    """

    def __init__(self, prefixes: Iterable[str] = None, keys: Iterable[str] = None):
        self.prefixes = set(prefixes or [])
        self.keys = set(keys or [])

    def update(self, other: "AttachmentKeys"):
        self.prefixes.update(other.prefixes)
        self.keys.update(other.keys)

    def is_empty(self) -> bool:
        return not self.prefixes and not self.keys

    def get_keys_outside_prefixes(self) -> List[str]:
        """
        The keys which are deleted by the prefixes are excluded
        """
        return sorted(key for key in self.keys if not key.startswith(tuple(self.prefixes)))


def get_cipher_attachment_prefix(user_internal_id, cipher_id) -> str:
    # The trailing slash prevents matching other ciphers whose id starts with this cipher id
    return f"attachments/{md5_encode(text=str(user_internal_id))}/{cipher_id}/"


def _parse_cipher_data(data) -> dict:
    if isinstance(data, dict):
        return data
    if not data:
        return {}
    try:
        parsed_data = ast.literal_eval(str(data))
    except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
        return {}
    return parsed_data if isinstance(parsed_data, dict) else {}


def extract_cipher_attachment_keys(cipher_id, internal_ids: Iterable, data) -> AttachmentKeys:
    """
    Get the attachment keys of a cipher
    :param cipher_id: (str) The cipher id
    :param internal_ids: (list) The internal ids of the cipher creator and the cipher owner
    :param data: (str|dict) The cipher data
    :return: AttachmentKeys
    """
    cipher_id = str(cipher_id)
    attachment_keys = AttachmentKeys()
    for internal_id in internal_ids:
        if internal_id:
            attachment_keys.prefixes.add(get_cipher_attachment_prefix(user_internal_id=internal_id, cipher_id=cipher_id))

    attachments = _parse_cipher_data(data).get("attachments") or []
    if not isinstance(attachments, list):
        return attachment_keys
    for attachment in attachments:
        if not isinstance(attachment, dict):
            continue
        key = normalize_attachment_key(attachment.get("url"))
        if not key:
            continue
        # The url is sent by the client. Only accept keys of this cipher, so a user can not delete files of others
        match = ATTACHMENT_KEY_PATTERN.fullmatch(key)
        if match and match.group("cipher_id") == cipher_id:
            attachment_keys.keys.add(key)
    return attachment_keys


def collect_attachment_keys(ciphers_orm) -> AttachmentKeys:
    """
    Collect the attachment keys of the ciphers. It must be called before deleting the ciphers
    :param ciphers_orm: CipherORM queryset
    :return: AttachmentKeys
    """
    attachment_keys = AttachmentKeys()
    ciphers = ciphers_orm.values("id", "data", "created_by__internal_id", "user__internal_id")
    for cipher in ciphers.iterator():
        attachment_keys.update(extract_cipher_attachment_keys(
            cipher_id=cipher.get("id"),
            internal_ids=[cipher.get("created_by__internal_id"), cipher.get("user__internal_id")],
            data=cipher.get("data")
        ))
    return attachment_keys


def _delete_attachment_keys(attachment_keys: AttachmentKeys):
    attachment_storage = AttachmentStorageFactory.get_attachment_service(
        service_name=locker_server_settings.DEFAULT_CLOUD_STORAGE
    )
    keys = attachment_keys.get_keys_outside_prefixes()
    if keys:
        attachment_storage.delete_files(file_paths=keys)
    for prefix in sorted(attachment_keys.prefixes):
        attachment_storage.delete_prefix(prefix=prefix)


def delete_attachment_keys(attachment_keys: Optional[AttachmentKeys], background: bool = True):
    """
    Delete the attachment files in the storage. The cipher rows should be deleted before
    :param attachment_keys: AttachmentKeys
    :param background: (bool) Run in a background thread (in the requests) or synchronously (in the cron jobs)
    """
    if attachment_keys is None or attachment_keys.is_empty():
        return
    if background:
        BackgroundThread(task=background_exception_wrapper(_delete_attachment_keys), attachment_keys=attachment_keys)
        return
    try:
        _delete_attachment_keys(attachment_keys=attachment_keys)
    except Exception:
        tb = traceback.format_exc()
        CyLog.error(**{"message": f"[!] Delete attachment files error: {tb}"})
