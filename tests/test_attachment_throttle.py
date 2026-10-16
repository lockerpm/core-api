from unittest.mock import MagicMock

from django.test import SimpleTestCase, override_settings
from rest_framework.settings import api_settings

from locker_server.api.v1_0.attachments.views import AttachmentPwdViewSet
from locker_server.shared.throttling.app import AppBaseThrottle


LOCMEM_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-attachment-throttle",
    }
}


def authenticated_request(user_id: int):
    request = MagicMock()
    request.auth.user.user_id = user_id
    return request


class AttachmentThrottleScopeTestCase(SimpleTestCase):
    def test_attachments_rate_is_configured(self):
        # A scope without a rate raises ImproperlyConfigured (HTTP 500)
        self.assertEqual(api_settings.DEFAULT_THROTTLE_RATES.get("attachments"), "30/min")

    def test_all_actions_use_attachments_scope(self):
        for action in ["create", "url", "multiple_delete"]:
            view = AttachmentPwdViewSet()
            view.request = authenticated_request(user_id=1)
            view.action = action
            view.get_throttles()
            self.assertEqual(view.throttle_scope, "attachments", action)


@override_settings(CACHES=LOCMEM_CACHES)
class AttachmentThrottleRateTestCase(SimpleTestCase):
    def setUp(self):
        AppBaseThrottle.cache.clear()
        self.view = MagicMock(throttle_scope="attachments")

    def allow_request(self, user_id: int) -> bool:
        # DRF creates a new throttle instance for each request
        return AppBaseThrottle().allow_request(authenticated_request(user_id=user_id), self.view)

    def test_31st_request_in_a_minute_is_throttled(self):
        for _ in range(30):
            self.assertTrue(self.allow_request(user_id=1))
        self.assertFalse(self.allow_request(user_id=1))

    def test_each_user_has_own_limit(self):
        for _ in range(30):
            self.allow_request(user_id=1)
        self.assertFalse(self.allow_request(user_id=1))
        self.assertTrue(self.allow_request(user_id=2))
