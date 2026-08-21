import time

import requests

from locker_server.shared.log.cylog import CyLog


XPOSEDORNOT_BREACH_ANALYTICS_API = "https://api.xposedornot.com/v1/breach-analytics"
DEFAULT_TIMEOUT = 10
DEFAULT_RETRY_DELAY = 3
MAX_RETRY_DELAY = 10


class XposedOrNotService:
    def __init__(self, retries_number=3, timeout=DEFAULT_TIMEOUT):
        self.retries_number = max(1, retries_number)
        self.timeout = timeout

    def check_breach(self, email):
        for attempt in range(self.retries_number):
            try:
                response = requests.get(
                    url=XPOSEDORNOT_BREACH_ANALYTICS_API,
                    params={"email": email},
                    headers={"Accept": "application/json", "User-Agent": "Locker"},
                    timeout=self.timeout,
                )
            except requests.exceptions.RequestException:
                CyLog.warning(**{"message": "[xposedornot] Request failed"})
                self._wait_before_retry(attempt, DEFAULT_RETRY_DELAY)
                continue

            if 200 <= response.status_code < 300:
                try:
                    return self._normalize_breaches(response.json())
                except (TypeError, ValueError):
                    CyLog.warning(**{"message": "[xposedornot] Invalid JSON response"})
                    return []

            if response.status_code == 429:
                retry_delay = self._get_retry_delay(response)
                CyLog.warning(**{"message": "[xposedornot] Rate limit exceeded"})
                self._wait_before_retry(attempt, retry_delay)
                continue

            if 500 <= response.status_code < 600:
                CyLog.warning(**{
                    "message": f"[xposedornot] Upstream error: {response.status_code}"
                })
                self._wait_before_retry(attempt, DEFAULT_RETRY_DELAY)
                continue

            CyLog.warning(**{
                "message": f"[xposedornot] Request rejected: {response.status_code}"
            })
            return []

        CyLog.error(**{"message": "[xposedornot] All breach check attempts failed"})
        return []

    def _wait_before_retry(self, attempt, delay):
        if attempt + 1 < self.retries_number:
            time.sleep(delay)

    @staticmethod
    def _get_retry_delay(response):
        try:
            delay = int(response.headers.get("Retry-After", DEFAULT_RETRY_DELAY))
        except (AttributeError, TypeError, ValueError):
            delay = DEFAULT_RETRY_DELAY
        return max(0, min(delay, MAX_RETRY_DELAY))

    @classmethod
    def _normalize_breaches(cls, payload):
        if not isinstance(payload, dict):
            return []

        exposed_breaches = payload.get("ExposedBreaches")
        if not isinstance(exposed_breaches, dict):
            return []

        breach_details = exposed_breaches.get("breaches_details")
        if not isinstance(breach_details, list):
            return []

        return [
            cls._normalize_breach(breach)
            for breach in breach_details
            if isinstance(breach, dict)
        ]

    @classmethod
    def _normalize_breach(cls, breach):
        breach_name = breach.get("breach")
        return {
            "name": breach_name,
            "title": breach_name,
            "domain": breach.get("domain"),
            "breach_date": breach.get("xposed_date"),
            "added_date": None,
            "modified_date": None,
            "pwn_count": breach.get("xposed_records"),
            "description": breach.get("details"),
            "data_classes": cls._normalize_data_classes(breach.get("xposed_data")),
            "is_verified": cls._normalize_boolean(breach.get("verified")),
            "is_fabricated": None,
            "is_sensitive": None,
            "is_retired": None,
            "is_spam_list": None,
            "is_malware": None,
            "is_subscription_free": None,
            "is_stealer_log": None,
            "logo_path": breach.get("logo"),
            "attribution": None,
        }

    @staticmethod
    def _normalize_data_classes(value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(";") if item.strip()]
        if isinstance(value, list):
            return value
        return []

    @staticmethod
    def _normalize_boolean(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized_value = value.strip().lower()
            if normalized_value in ["yes", "true", "1"]:
                return True
            if normalized_value in ["no", "false", "0"]:
                return False
        return None
