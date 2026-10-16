import re
from typing import Optional, Tuple
from urllib.parse import urlparse


# Attachment key format: attachments/{md5(user internal_id)}/{cipher_id}/{attachment_id}
ATTACHMENT_KEY_PATTERN = re.compile(r"attachments/[0-9a-f]{32}/(?P<cipher_id>[^/]+)/\d+")


def normalize_attachment_key(url) -> Optional[str]:
    """
    Get the storage key from an attachment url. The url can be a key or a full url (with the bucket name)
    """
    if not url or not isinstance(url, str):
        return None
    path = urlparse(url).path if "://" in url else url
    index = path.find("attachments/")
    if index < 0:
        return None
    return path[index:]


def parse_attachment_key(url) -> Optional[Tuple[str, str]]:
    """
    Parse an attachment url/key
    :param url: (str) The attachment key or the full attachment url
    :return: (tuple) The normalized key and the cipher id, or None if the url is not a valid attachment key
    """
    key = normalize_attachment_key(url)
    if not key:
        return None
    match = ATTACHMENT_KEY_PATTERN.fullmatch(key)
    if not match:
        return None
    return key, match.group("cipher_id")
