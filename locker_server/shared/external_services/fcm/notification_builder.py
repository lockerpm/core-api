import re
from typing import Dict, List, Optional

from locker_server.shared.constants.ciphers import MAP_CIPHER_TYPE_STR, CIPHER_TYPE_LOGIN, CIPHER_TYPE_NOTE, \
    CIPHER_TYPE_CARD, CIPHER_TYPE_IDENTITY, CIPHER_TYPE_TOTP, CIPHER_TYPE_CRYPTO_ACCOUNT, CIPHER_TYPE_CRYPTO_WALLET, \
    CIPHER_TYPE_DRIVER_LICENSE, CIPHER_TYPE_CITIZEN_ID, CIPHER_TYPE_PASSPORT, CIPHER_TYPE_SOCIAL_SECURITY_NUMBER, \
    CIPHER_TYPE_WIRELESS_ROUTER, CIPHER_TYPE_SERVER, CIPHER_TYPE_API, CIPHER_TYPE_DATABASE
from locker_server.shared.constants.emergency_access import EMERGENCY_ACCESS_TYPE_VIEW, EMERGENCY_ACCESS_TYPE_TAKEOVER
from locker_server.shared.constants.lang import LANG_ENGLISH, LANG_VIETNAM
from locker_server.shared.external_services.fcm.constants import FCM_NOTIFICATIONS
from locker_server.shared.external_services.fcm.fcm_request_entity import FCMRequestEntity
from locker_server.shared.external_services.fcm.fcm_sender import FCMSenderService


SUPPORTED_FCM_LANGUAGES = [LANG_ENGLISH, LANG_VIETNAM]

# The FCM_NOTIFICATIONS templates are rendered with this pattern instead of str.format: not every payload carries
# every placeholder of its template, and a substitution simply leaves those empty
PLACEHOLDER_REG = re.compile(r"\{(\w+)\}")

SHARE_TYPE_NAME = {
    LANG_ENGLISH: dict(MAP_CIPHER_TYPE_STR, **{"folder": "folder"}),
    LANG_VIETNAM: {
        "folder": "thư mục",
        CIPHER_TYPE_LOGIN: "mật khẩu",
        CIPHER_TYPE_NOTE: "ghi chú",
        CIPHER_TYPE_CARD: "thẻ",
        CIPHER_TYPE_IDENTITY: "danh tính",
        CIPHER_TYPE_TOTP: "mã xác thực",
        CIPHER_TYPE_CRYPTO_ACCOUNT: "tài khoản crypto",
        CIPHER_TYPE_CRYPTO_WALLET: "ví crypto",
        CIPHER_TYPE_DRIVER_LICENSE: "giấy phép lái xe",
        CIPHER_TYPE_CITIZEN_ID: "căn cước công dân",
        CIPHER_TYPE_PASSPORT: "hộ chiếu",
        CIPHER_TYPE_SOCIAL_SECURITY_NUMBER: "số an sinh xã hội",
        CIPHER_TYPE_WIRELESS_ROUTER: "bộ định tuyến",
        CIPHER_TYPE_SERVER: "máy chủ",
        CIPHER_TYPE_API: "api",
        CIPHER_TYPE_DATABASE: "cơ sở dữ liệu",
    }
}

DEFAULT_SHARE_TYPE_NAME = {
    LANG_ENGLISH: "item",
    LANG_VIETNAM: "mục"
}

EMERGENCY_TYPE_NAME = {
    LANG_ENGLISH: {
        EMERGENCY_ACCESS_TYPE_VIEW: "view",
        EMERGENCY_ACCESS_TYPE_TAKEOVER: "take over"
    },
    LANG_VIETNAM: {
        EMERGENCY_ACCESS_TYPE_VIEW: "xem",
        EMERGENCY_ACCESS_TYPE_TAKEOVER: "tiếp quản"
    }
}


def normalize_fcm_language(language) -> str:
    """
    Map any stored user language onto a language that FCM_NOTIFICATIONS has copy for
    :param language: (str) The raw `user.language` value
    :return: (str) LANG_ENGLISH or LANG_VIETNAM
    """
    normalized_language = (language or "").strip().lower()
    if normalized_language not in SUPPORTED_FCM_LANGUAGES:
        return LANG_ENGLISH
    return normalized_language


def render_notification_template(template: str, params: Dict) -> str:
    """
    Replace the `{placeholder}` slots of a notification template. A placeholder that the payload does not carry
    renders empty instead of raising
    :param template: (str) The raw template from FCM_NOTIFICATIONS
    :param params: (dict) The values to interpolate
    :return: (str)
    """
    if not template:
        return ""
    rendered = PLACEHOLDER_REG.sub(lambda match: str(params.get(match.group(1), "") or ""), template)
    # An empty slot leaves the spaces around it behind
    return " ".join(rendered.split())


def build_notification_params(language: str, data: Dict = None) -> Dict:
    """
    Derive the template placeholders that the FCM payloads do not carry verbatim
    :param language: (str) A normalized language
    :param data: (dict) The inner FCM data payload
    :return: (dict)
    """
    params = dict(data or {})
    if not params.get("type_name"):
        params["type_name"] = SHARE_TYPE_NAME.get(language, {}).get(
            params.get("share_type"), DEFAULT_SHARE_TYPE_NAME.get(language)
        )
    emergency_type_name = EMERGENCY_TYPE_NAME.get(language, {}).get(params.get("type"))
    if emergency_type_name:
        params["type"] = emergency_type_name
    return params


def build_fcm_notification(event: str, language: str = None, data: Dict = None) -> Optional[Dict]:
    """
    Build the displayed title/body of an FCM message in the recipient's language
    :param event: (str) A FCM_TYPE_* event
    :param language: (str) The recipient `user.language`
    :param data: (dict) The inner FCM data payload
    :return: (dict) {"title": ..., "body": ...} or None when the event has no copy
    """
    event_notifications = FCM_NOTIFICATIONS.get(event)
    if not event_notifications:
        return None
    normalized_language = normalize_fcm_language(language)
    notification = event_notifications.get(normalized_language) or event_notifications.get(LANG_ENGLISH)
    if not notification:
        return None
    params = build_notification_params(language=normalized_language, data=data)
    body = render_notification_template(template=notification.get("body"), params=params)
    if not body:
        return None
    return {
        "title": render_notification_template(template=notification.get("title"), params=params),
        "body": body
    }


def send_localized_fcm(lang_fcm_ids: Dict[str, List[str]], event: str, data: Dict = None, priority: str = "high",
                       is_background: bool = True):
    """
    Send an FCM message per language group, each carrying the notification copy of that language in its data part
    :param lang_fcm_ids: (dict) {language: [fcm_id]}, from `get_lang_fcm_ids_by_user_ids`. The languages are the raw
                         `user.language` values: groups that share notification copy are merged here
    :param event: (str) A FCM_TYPE_* event
    :param data: (dict) The inner FCM data payload
    :param priority: (str)
    :param is_background: (bool) Send in a background thread or not
    """
    normalized_lang_fcm_ids = {}
    for language, fcm_ids in (lang_fcm_ids or {}).items():
        normalized_lang_fcm_ids.setdefault(normalize_fcm_language(language), []).extend(fcm_ids or [])

    for language, fcm_ids in normalized_lang_fcm_ids.items():
        if not fcm_ids:
            continue
        # The sender re-encodes the data part in place, so each group gets its own copy
        message_data = {"event": event, "data": dict(data or {})}
        notification = build_fcm_notification(event=event, language=language, data=data)
        if notification:
            # The notification travels inside the data part: the client reads it from there and displays it
            message_data["notification"] = notification
        fcm_message = FCMRequestEntity(fcm_ids=list(fcm_ids), priority=priority, data=message_data)
        FCMSenderService(is_background=is_background).run("send_message", **{"fcm_message": fcm_message})
