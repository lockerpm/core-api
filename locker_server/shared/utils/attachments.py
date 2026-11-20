import base64
import binascii
import hashlib
import hmac
import re
import time
from typing import Optional, Tuple
from urllib.parse import quote, unquote, urlparse, urlsplit


# Attachment key format: attachments/{md5(user internal_id)}/{cipher_id}/{attachment_id}
ATTACHMENT_KEY_PATTERN = re.compile(r"attachments/[0-9a-f]{32}/(?P<cipher_id>[^/]+)/\d+")

# The CDN url signature (Cloudflare token authentication: is_timed_hmac_valid_v0): <path>?verify=<timestamp>-<mac>
CDN_URL_SIGNATURE_PARAM = "verify"
CDN_URL_SIGNATURE_SEPARATOR = f"?{CDN_URL_SIGNATURE_PARAM}="


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


def _cdn_url_mac(secret: str, message: str, timestamp: int) -> bytes:
    return hmac.new(secret.encode("utf-8"), f"{message}{timestamp}".encode("utf-8"), hashlib.sha256).digest()


def sign_cdn_url(base_url: str, file_path: str, secret: str, timestamp: int = None) -> str:
    """
    Sign a CDN url, so the edge (the Cloudflare WAF rule with is_timed_hmac_valid_v0) only serves the file until the
    url expires. The TTL is set in the WAF rule, not here
    :param base_url: (str) The CDN url, e.g. https://files.locker.io
    :param file_path: (str) The storage key
    :param secret: (str) The HMAC secret, the same as the secret of the WAF rule
    :param timestamp: (int) The signing time (seconds). Default: now
    :return: (str) <base_url>/<file_path>?verify=<timestamp>-<url encoded base64 mac>
    """
    # The signed message must be exactly the request uri path which the edge receives
    path = "/" + quote(file_path.lstrip("/"))
    timestamp = int(time.time()) if timestamp is None else int(timestamp)
    mac = base64.b64encode(_cdn_url_mac(secret=secret, message=path, timestamp=timestamp)).decode("utf-8")
    return f"{base_url.rstrip('/')}{path}{CDN_URL_SIGNATURE_SEPARATOR}{timestamp}-{quote(mac, safe='')}"


def verify_cdn_url(url: str, secret: str, ttl: int, current_timestamp: int = None) -> bool:
    """
    Verify a signed CDN url as the edge does (is_timed_hmac_valid_v0 on http.request.uri, separator ?verify=).
    It is used to check the signed urls (tests, debugging), the requests are verified by the edge
    """
    if not url or not secret:
        return False
    split_url = urlsplit(url)
    uri = f"{split_url.path}?{split_url.query}" if split_url.query else split_url.path
    index = uri.rfind(CDN_URL_SIGNATURE_SEPARATOR)
    if index < 0:
        return False
    message = uri[:index]
    timestamp, _, encoded_mac = uri[index + len(CDN_URL_SIGNATURE_SEPARATOR):].partition("-")
    if not timestamp.isdigit() or not encoded_mac:
        return False
    try:
        mac = base64.b64decode(unquote(encoded_mac), validate=True)
    except (binascii.Error, ValueError):
        return False
    current_timestamp = int(time.time()) if current_timestamp is None else int(current_timestamp)
    if not 0 <= current_timestamp - int(timestamp) <= ttl:
        return False
    return hmac.compare_digest(mac, _cdn_url_mac(secret=secret, message=message, timestamp=int(timestamp)))
