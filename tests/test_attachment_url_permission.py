from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from locker_server.api.permissions.locker_permissions.attachment_permission import AttachmentPwdPermission
from locker_server.api.v1_0.attachments.views import AttachmentPwdViewSet
from locker_server.core.entities.user.user import User
from locker_server.shared.constants.emergency_access import EMERGENCY_ACCESS_TYPE_VIEW, \
    EMERGENCY_ACCESS_TYPE_TAKEOVER, EMERGENCY_ACCESS_STATUS_RECOVERY_APPROVED, \
    EMERGENCY_ACCESS_STATUS_RECOVERY_INITIATED
from locker_server.shared.utils.attachments import parse_attachment_key


USER_ID = 1
GRANTOR_ID = 2
CIPHER_ID = "b5316c03-5e88-4714-b7f4-2a02b54f7de3"
OTHER_CIPHER_ID = "a540c59c-3e3c-4c00-8b87-a0b9005e39ae"
ATTACHMENT_KEY = f"attachments/15204d27717c9b239e97720aee8fc037/{CIPHER_ID}/12252476111598511924"


def emergency_access(emergency_access_type: str, status_value: str, grantor_id: int = GRANTOR_ID):
    return MagicMock(
        emergency_access_type=emergency_access_type, status=status_value, grantor=MagicMock(user_id=grantor_id)
    )


class ParseAttachmentKeyTestCase(SimpleTestCase):
    def test_valid_key(self):
        self.assertEqual(parse_attachment_key(ATTACHMENT_KEY), (ATTACHMENT_KEY, CIPHER_ID))

    def test_full_url_is_normalized(self):
        for url in [f"https://files.locker.io/{ATTACHMENT_KEY}",
                    f"https://abc.r2.cloudflarestorage.com/lockerio/{ATTACHMENT_KEY}?X-Amz-Signature=xyz"]:
            self.assertEqual(parse_attachment_key(url), (ATTACHMENT_KEY, CIPHER_ID))

    def test_invalid_keys(self):
        for path in [None, "", "abc", "attachments/", "attachments/../x",
                     f"attachments/15204d27717c9b239e97720aee8fc037/{CIPHER_ID}",
                     f"attachments/15204d27717c9b239e97720aee8fc037/{CIPHER_ID}/",
                     f"attachments/15204d27717c9b239e97720aee8fc037/{CIPHER_ID}/../{OTHER_CIPHER_ID}/1",
                     f"attachments/not-a-md5/{CIPHER_ID}/1"]:
            self.assertIsNone(parse_attachment_key(path), path)


@override_settings(SELF_HOSTED=True, SECRET_KEY="test-secret")
class AttachmentUrlPermissionTestCase(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User(user_id=USER_ID, email="user@example.com", activated=True)
        self.cipher_service = MagicMock()
        self.cipher_service.get_multiple_by_user.return_value = []
        self.emergency_access_service = MagicMock()
        self.emergency_access_service.list_by_grantee_id.return_value = []
        self.attachment_service = MagicMock()
        self.attachment_service.get_onetime_url.return_value = "https://files.locker.io/signed"
        self.quick_share_service = MagicMock()

    def _post_url(self, path):
        view = AttachmentPwdViewSet.as_view({"post": "url"})
        request = self.factory.post("/v3/cystack_platform/pm/attachments/url", {"path": path}, format="json")
        force_authenticate(request, user=self.user)
        with patch.object(AttachmentPwdViewSet, "cipher_service", self.cipher_service), \
                patch.object(AttachmentPwdViewSet, "emergency_access_service", self.emergency_access_service), \
                patch.object(AttachmentPwdViewSet, "attachment_service", self.attachment_service), \
                patch.object(AttachmentPwdViewSet, "quick_share_service", self.quick_share_service), \
                patch.object(AttachmentPwdViewSet, "get_throttles", return_value=[]), \
                patch.object(AttachmentPwdPermission, "has_permission", return_value=True):
            return view(request)

    def _vault_of(self, *user_ids):
        # The ciphers in the vault of these users contain CIPHER_ID
        def get_multiple_by_user(user_id, filter_ids=None, **kwargs):
            return [MagicMock()] if user_id in user_ids and filter_ids == [CIPHER_ID] else []
        return get_multiple_by_user

    def assert_signed(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"url": "https://files.locker.io/signed"})
        self.assertEqual(self.attachment_service.get_onetime_url.call_args.kwargs["path"], ATTACHMENT_KEY)

    def assert_not_found(self, response):
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.attachment_service.get_onetime_url.assert_not_called()

    def test_owner_or_team_member_can_get_url(self):
        self.cipher_service.get_multiple_by_user.side_effect = self._vault_of(USER_ID)
        self.assert_signed(self._post_url(ATTACHMENT_KEY))

    def test_other_user_can_not_get_url(self):
        # The PoC of the IDOR report: the attacker requests the path of a victim's attachment
        self.assert_not_found(self._post_url(ATTACHMENT_KEY))

    def test_emergency_access_view_grantee_can_get_url(self):
        self.cipher_service.get_multiple_by_user.side_effect = self._vault_of(GRANTOR_ID)
        self.emergency_access_service.list_by_grantee_id.return_value = [
            emergency_access(EMERGENCY_ACCESS_TYPE_VIEW, EMERGENCY_ACCESS_STATUS_RECOVERY_APPROVED)
        ]
        self.assert_signed(self._post_url(ATTACHMENT_KEY))
        self.emergency_access_service.list_by_grantee_id.assert_called_once_with(grantee_id=USER_ID)

    def test_not_approved_or_takeover_emergency_access_can_not_get_url(self):
        self.cipher_service.get_multiple_by_user.side_effect = self._vault_of(GRANTOR_ID)
        self.emergency_access_service.list_by_grantee_id.return_value = [
            emergency_access(EMERGENCY_ACCESS_TYPE_VIEW, EMERGENCY_ACCESS_STATUS_RECOVERY_INITIATED),
            emergency_access(EMERGENCY_ACCESS_TYPE_TAKEOVER, EMERGENCY_ACCESS_STATUS_RECOVERY_APPROVED),
        ]
        self.assert_not_found(self._post_url(ATTACHMENT_KEY))

    def test_emergency_access_does_not_cover_other_grantors(self):
        self.cipher_service.get_multiple_by_user.side_effect = self._vault_of(GRANTOR_ID)
        self.emergency_access_service.list_by_grantee_id.return_value = [
            emergency_access(EMERGENCY_ACCESS_TYPE_VIEW, EMERGENCY_ACCESS_STATUS_RECOVERY_APPROVED, grantor_id=3)
        ]
        self.assert_not_found(self._post_url(ATTACHMENT_KEY))

    def test_public_quick_share_does_not_grant_access(self):
        # The cipher is publicly quick shared, but its attachments are not shared with anyone
        self.quick_share_service.list_by_cipher_id.return_value = [MagicMock(is_public=True)]
        self.assert_not_found(self._post_url(ATTACHMENT_KEY))
        self.assertEqual(self.quick_share_service.method_calls, [])

    def test_invalid_paths_return_not_found(self):
        for path in ["attachments/../x", f"attachments/15204d27717c9b239e97720aee8fc037/{CIPHER_ID}",
                     "https://evil.com/anything"]:
            self.assert_not_found(self._post_url(path))
        self.cipher_service.get_multiple_by_user.assert_not_called()

    def test_full_url_is_normalized_before_signing(self):
        self.cipher_service.get_multiple_by_user.side_effect = self._vault_of(USER_ID)
        self.assert_signed(self._post_url(f"https://files.locker.io/{ATTACHMENT_KEY}"))
