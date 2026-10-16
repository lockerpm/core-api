from django.core.cache import cache

from locker_server.shared.utils.app import now


# The quota of the issued upload forms is reserved until the forms expire, because the presigned PUT urls do not limit
# the file size. Note:
# - Reading and writing the reservations is not atomic: two concurrent requests may reserve one more form
# - If the cache is not available, the reservations are ignored (fail-open)


def get_attachment_reservations_cache_key(user_key: str) -> str:
    return f"attachment_upload_reservations:{user_key}"


def _get_active_reservations(user_key: str) -> dict:
    reservations = cache.get(get_attachment_reservations_cache_key(user_key=user_key)) or {}
    current_time = now()
    return {
        upload_key: (expired_time, size) for upload_key, (expired_time, size) in reservations.items()
        if expired_time > current_time
    }


def get_reserved_upload_size(user_key: str) -> int:
    return sum(size or 0 for _, size in _get_active_reservations(user_key=user_key).values())


def reserve_upload(user_key: str, upload_key: str, size: int, expires_in: int):
    reservations = _get_active_reservations(user_key=user_key)
    reservations[upload_key] = (now() + expires_in, size or 0)
    cache.set(get_attachment_reservations_cache_key(user_key=user_key), reservations, timeout=expires_in)
