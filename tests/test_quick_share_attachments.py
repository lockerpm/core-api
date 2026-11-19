from unittest.mock import MagicMock, patch

import jwt
from django.test import SimpleTestCase, override_settings
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from locker_server.api.permissions.locker_permissions.quick_share_pwd_permission import QuickSharePwdPermission
from locker_server.api.v1_0.quick_shares.serializers import CreateQuickShareSerializer, ListQuickShareSerializer, \
    PublicAccessQuickShareSerializer
from locker_server.api.v1_0.quick_shares.views import QuickSharePwdViewSet
from locker_server.api_orm.model_parsers.quick_share_parser import QuickShareParser
from locker_server.api_orm.repositories.quick_share_repository import QuickShareORMRepository
from locker_server.core.entities.quick_share.quick_share import QuickShare
from locker_server.core.entities.user.user import User
from locker_server.core.exceptions.cipher_exception import CipherDoesNotExistException
from locker_server.core.exceptions.quick_share_exception import QuickShareAttachmentNotValidException, \
    QuickShareNotValidAccessException, QuickShareRequireOTPException
from locker_server.core.services.quick_share_service import QuickShareService
from locker_server.shared.constants.attachments import QUICK_SHARE_ATTACHMENT_URL_EXPIRED
from locker_server.shared.constants.ciphers import CIPHER_TYPE_LOGIN
from locker_server.shared.constants.token import TOKEN_TYPE_QUICK_SHARE_ACCESS, TOKEN_TYPE_QUICK_SHARE_ATTACHMENT
from locker_server.shared.utils.app import now


SECRET_KEY = "test-secret-key-for-quick-share-attachments"
USER_ID = 1
CIPHER_ID = "b5316c03-5e88-4714-b7f4-2a02b54f7de3"
OTHER_CIPHER_ID = "a540c59c-3e3c-4c00-8b87-a0b9005e39ae"
USER_HASH = "15204d27717c9b239e97720aee8fc037"
ATTACHMENT_KEY = f"attachments/{USER_HASH}/{CIPHER_ID}/12252476111598511924"
OTHER_ATTACHMENT_KEY = f"attachments/{USER_HASH}/{CIPHER_ID}/99999999999999999999"
ACCESS_ID = "0123456789ABCDEF0123456789ABCDEF"
EMAIL = "recipient@example.com"


def attachment(attachment_id="a1", url=ATTACHMENT_KEY):
    return {"id": attachment_id, "url": url, "size": 10.0, "fileName": "enc-name", "key": "enc-key"}


def cipher_mock(attachments=None, cipher_id=CIPHER_ID):
    return MagicMock(cipher_id=cipher_id, data={"name": "enc", "attachments": attachments})


def quick_share_entity(attachments=None, cipher_attachments=None, is_public=True, emails=None, disabled=False,
                       expiration_date=None, max_access_count=None, access_count=0):
    attachments = [attachment()] if attachments is None else attachments
    cipher_attachments = attachments if cipher_attachments is None else cipher_attachments
    return QuickShare(
        quick_share_id="qs-1", cipher=cipher_mock(attachments=cipher_attachments), access_id=ACCESS_ID,
        quick_share_type=CIPHER_TYPE_LOGIN,
        data={"username": "enc", "name": "enc", "fields": None, "attachments": attachments},
        key="enc-key", is_public=is_public, emails=emails or [], disabled=disabled,
        expiration_date=expiration_date, max_access_count=max_access_count, access_count=access_count,
    )


def make_service(quick_share_repository=None, cipher_repository=None):
    if quick_share_repository is None:
        real_repository = QuickShareORMRepository()
        quick_share_repository = MagicMock()
        quick_share_repository.generate_attachment_access_token.side_effect = \
            real_repository.generate_attachment_access_token
        quick_share_repository.validate_attachment_access_token.side_effect = \
            real_repository.validate_attachment_access_token
    return QuickShareService(
        quick_share_repository=quick_share_repository, cipher_repository=cipher_repository or MagicMock(),
        user_repository=MagicMock(), enterprise_repository=MagicMock()
    )


@override_settings(SECRET_KEY=SECRET_KEY)
class AttachmentTokenTestCase(SimpleTestCase):
    def setUp(self):
        self.repository = QuickShareORMRepository()
        self.quick_share = quick_share_entity()

    def test_generate_and_validate(self):
        token, expired_time = self.repository.generate_attachment_access_token(quick_share=self.quick_share, email=EMAIL)
        self.assertGreater(expired_time, now())
        payload = self.repository.validate_attachment_access_token(quick_share=self.quick_share, token=token)
        self.assertEqual(payload["email"], EMAIL)
        self.assertEqual(payload["access_id"], ACCESS_ID)

    def test_invalid_tokens(self):
        other_share = quick_share_entity()
        other_share._access_id = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
        other_token, _ = self.repository.generate_attachment_access_token(quick_share=other_share)
        valid_token, _ = self.repository.generate_attachment_access_token(quick_share=self.quick_share)
        tokens = [
            # The token of another quick share
            other_token,
            # Expired
            jwt.encode({"token_type": TOKEN_TYPE_QUICK_SHARE_ATTACHMENT, "access_id": ACCESS_ID, "exp": int(now()) - 1},
                       SECRET_KEY, algorithm="HS256"),
            # Without the exp claim
            jwt.encode({"token_type": TOKEN_TYPE_QUICK_SHARE_ATTACHMENT, "access_id": ACCESS_ID},
                       SECRET_KEY, algorithm="HS256"),
            # The public access token of the quick share (wrong token type)
            jwt.encode({"token_type": TOKEN_TYPE_QUICK_SHARE_ACCESS, "access_id": ACCESS_ID, "email": EMAIL,
                        "expired_time": now() + 3600, "exp": int(now()) + 3600}, SECRET_KEY, algorithm="HS256"),
            # Signed by another key
            jwt.encode({"token_type": TOKEN_TYPE_QUICK_SHARE_ATTACHMENT, "access_id": ACCESS_ID,
                        "exp": int(now()) + 3600}, "other-secret-key-for-quick-share-attachments", algorithm="HS256"),
            # Tampered signature
            valid_token[:-2] + ("AA" if not valid_token.endswith("AA") else "BB"),
            "not-a-token",
            "",
        ]
        for token in tokens:
            self.assertIsNone(
                self.repository.validate_attachment_access_token(quick_share=self.quick_share, token=token), token
            )


@override_settings(SECRET_KEY=SECRET_KEY)
class QuickShareAttachmentServiceTestCase(SimpleTestCase):
    def setUp(self):
        self.cipher_repository = MagicMock()
        self.cipher_repository.get_multiple_by_user.return_value = [MagicMock()]
        self.cipher_repository.get_by_id.return_value = cipher_mock(attachments=[attachment()])
        self.service = make_service(cipher_repository=self.cipher_repository)

    # ------------------------ Create ------------------------ #
    def _validate(self, attachments):
        quick_share_data = {"cipher_id": CIPHER_ID, "data": {"name": "enc", "attachments": attachments}}
        return self.service._validate_quick_share_attachments(user_id=USER_ID, quick_share_data=quick_share_data)

    def test_create_normalizes_attachment_urls(self):
        result = self._validate([attachment(url=f"https://files.locker.io/{ATTACHMENT_KEY}?X-Amz-Signature=x")])
        self.assertEqual(result["data"]["attachments"], [attachment()])
        self.cipher_repository.get_multiple_by_user.assert_called_once_with(user_id=USER_ID, filter_ids=[CIPHER_ID])

    def test_create_without_attachments_does_not_check_the_cipher(self):
        for attachments in [None, []]:
            self.assertEqual(self._validate(attachments)["data"]["attachments"], attachments)
        self.cipher_repository.get_multiple_by_user.assert_not_called()

    def test_create_rejects_invalid_attachments(self):
        invalid_attachments_list = [
            # The attachment of another cipher
            [attachment(url=f"attachments/{USER_HASH}/{OTHER_CIPHER_ID}/1")],
            # The attachment is not in the cipher data (e.g. removed from the cipher)
            [attachment(url=OTHER_ATTACHMENT_KEY)],
            # Not an attachment key
            [attachment(url="https://evil.com/anything")],
            [attachment(url=f"attachments/{USER_HASH}/{CIPHER_ID}/../{OTHER_CIPHER_ID}/1")],
            # The duplicated ids
            [attachment(), attachment()],
        ]
        self.cipher_repository.get_by_id.return_value = cipher_mock(
            attachments=[attachment(), attachment("a2", url=f"attachments/{USER_HASH}/{OTHER_CIPHER_ID}/1")]
        )
        for attachments in invalid_attachments_list:
            with self.assertRaises(QuickShareAttachmentNotValidException, msg=attachments):
                self._validate(attachments)

    def test_create_requires_the_user_can_view_the_cipher(self):
        # E.g. the member created the cipher in a sharing folder, then left the sharing team
        self.cipher_repository.get_multiple_by_user.return_value = []
        with self.assertRaises(CipherDoesNotExistException):
            self._validate([attachment()])

    # ------------------------ Token ------------------------ #
    def test_issue_token_only_when_the_quick_share_has_attachments(self):
        self.assertIsNotNone(self.service.issue_attachment_token(quick_share=quick_share_entity()))
        self.assertIsNone(self.service.issue_attachment_token(quick_share=quick_share_entity(attachments=[])))

    def _token(self, quick_share, email=None):
        token, _ = self.service.issue_attachment_token(quick_share=quick_share, email=email)
        return token

    def test_get_attachment_path(self):
        quick_share = quick_share_entity()
        path = self.service.get_attachment_path(
            quick_share=quick_share, attachment_id="a1", attachment_token=self._token(quick_share)
        )
        self.assertEqual(path, ATTACHMENT_KEY)
        self.service.quick_share_repository.update_access_count.assert_not_called()

    def test_max_access_count_does_not_block_the_download(self):
        # The access is counted when the token is issued
        quick_share = quick_share_entity(max_access_count=1, access_count=1)
        self.assertEqual(self.service.get_attachment_path(
            quick_share=quick_share, attachment_id="a1", attachment_token=self._token(quick_share)
        ), ATTACHMENT_KEY)

    def test_not_available_quick_share(self):
        for quick_share in [quick_share_entity(disabled=True), quick_share_entity(expiration_date=now() - 1)]:
            with self.assertRaises(QuickShareNotValidAccessException):
                self.service.get_attachment_path(
                    quick_share=quick_share, attachment_id="a1", attachment_token=self._token(quick_share)
                )

    def test_private_quick_share_requires_the_email_in_the_token(self):
        quick_share = quick_share_entity(is_public=False, emails=[{"email": EMAIL}])
        self.assertEqual(self.service.get_attachment_path(
            quick_share=quick_share, attachment_id="a1", attachment_token=self._token(quick_share, email=EMAIL)
        ), ATTACHMENT_KEY)
        for email in [None, "other@example.com"]:
            with self.assertRaises(QuickShareNotValidAccessException):
                self.service.get_attachment_path(
                    quick_share=quick_share, attachment_id="a1", attachment_token=self._token(quick_share, email)
                )
        # The email is removed from the quick share
        removed_email_share = quick_share_entity(is_public=False, emails=[{"email": "other@example.com"}])
        with self.assertRaises(QuickShareNotValidAccessException):
            self.service.get_attachment_path(
                quick_share=removed_email_share, attachment_id="a1",
                attachment_token=self._token(removed_email_share, email=EMAIL)
            )

    def test_invalid_token(self):
        quick_share = quick_share_entity()
        with self.assertRaises(QuickShareNotValidAccessException):
            self.service.get_attachment_path(quick_share=quick_share, attachment_id="a1", attachment_token="invalid")

    def test_attachment_does_not_belong_to_the_quick_share(self):
        quick_share = quick_share_entity()
        with self.assertRaises(QuickShareAttachmentNotValidException):
            self.service.get_attachment_path(
                quick_share=quick_share, attachment_id="unknown", attachment_token=self._token(quick_share)
            )

    def test_attachment_is_removed_from_the_cipher(self):
        quick_share = quick_share_entity(cipher_attachments=[attachment("a2", url=OTHER_ATTACHMENT_KEY)])
        with self.assertRaises(QuickShareAttachmentNotValidException):
            self.service.get_attachment_path(
                quick_share=quick_share, attachment_id="a1", attachment_token=self._token(quick_share)
            )

    # ------------------------ Disabled ------------------------ #
    def test_get_email_access_of_disabled_quick_share(self):
        for is_public in [True, False]:
            with self.assertRaises(QuickShareNotValidAccessException):
                self.service.get_email_access(quick_share=quick_share_entity(disabled=True, is_public=is_public))
        with self.assertRaises(QuickShareRequireOTPException):
            self.service.get_email_access(quick_share=quick_share_entity(is_public=False))


class QuickShareSerializerTestCase(SimpleTestCase):
    def test_create_serializer_accepts_attachments(self):
        serializer = CreateQuickShareSerializer(data={
            "cipher_id": CIPHER_ID, "key": "enc-key",
            "cipher": {"type": CIPHER_TYPE_LOGIN, "name": "enc", "notes": None, "login": {"username": "enc", "password": "enc", "totp": None, "uris": None},
                       "attachments": [attachment()]},
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        data = serializer.save()
        self.assertEqual([dict(a) for a in data["data"]["attachments"]], [attachment()])

    def test_owner_sees_the_attachment_urls(self):
        result = ListQuickShareSerializer(quick_share_entity()).data
        self.assertEqual(result["cipher"]["attachments"], [attachment()])

    def test_public_response_does_not_contain_the_attachment_urls(self):
        result = PublicAccessQuickShareSerializer(quick_share_entity()).data
        self.assertEqual(result["cipher"]["attachments"], [
            {"id": "a1", "size": 10.0, "fileName": "enc-name", "key": "enc-key"}
        ])
        self.assertNotIn(ATTACHMENT_KEY, str(result))


class QuickShareDisabledTestCase(SimpleTestCase):
    def test_parser_returns_boolean(self):
        cipher_parser = MagicMock()
        with patch("locker_server.api_orm.model_parsers.quick_share_parser.get_specific_model_parser",
                   return_value=cipher_parser):
            for value, expected in [(1.0, True), (0.0, False), (True, True), (False, False)]:
                quick_share_orm = MagicMock(disabled=value)
                quick_share_orm.get_data.return_value = {}
                self.assertIs(QuickShareParser.parse_quick_share(quick_share_orm).disabled, expected)

    def test_check_valid_access_of_disabled_quick_share(self):
        repository = QuickShareORMRepository()
        self.assertFalse(repository.check_valid_access(quick_share=quick_share_entity(disabled=True)))
        self.assertTrue(repository.check_valid_access(quick_share=quick_share_entity()))

    def _update(self, **quick_share_data):
        quick_share_orm = MagicMock(disabled=True, require_otp=True, is_public=False)
        quick_share_orm.quick_share_emails.values_list.return_value = [EMAIL]
        repository = QuickShareORMRepository()
        with patch.object(QuickShareORMRepository, "_get_quick_share_orm", return_value=quick_share_orm), \
                patch("locker_server.api_orm.repositories.quick_share_repository.ModelParser"):
            repository.update_quick_share(quick_share_id="qs-1", **quick_share_data)
        return quick_share_orm

    def test_update_can_set_the_flags_to_false(self):
        quick_share_orm = self._update(disabled=False, require_otp=False, is_public=True)
        self.assertIs(quick_share_orm.disabled, False)
        self.assertIs(quick_share_orm.require_otp, False)
        self.assertIs(quick_share_orm.is_public, True)

    def test_update_keeps_the_flags_when_they_are_not_given(self):
        quick_share_orm = self._update()
        self.assertIs(quick_share_orm.disabled, True)
        self.assertIs(quick_share_orm.require_otp, True)
        self.assertIs(quick_share_orm.is_public, False)

    def test_update_without_emails_does_not_remove_the_emails(self):
        quick_share_orm = self._update(disabled=True)
        quick_share_orm.quick_share_emails.filter.assert_not_called()
        quick_share_orm = self._update(emails=[])
        quick_share_orm.quick_share_emails.filter.assert_called_once_with(email__in=[EMAIL])


@override_settings(SELF_HOSTED=True, SECRET_KEY=SECRET_KEY)
class QuickShareAttachmentViewTestCase(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.quick_share = quick_share_entity()
        self.quick_share_service = MagicMock()
        self.quick_share_service.get_by_access_id.return_value = self.quick_share
        self.quick_share_service.get_attachment_path.return_value = ATTACHMENT_KEY
        self.attachment_service = MagicMock()
        self.attachment_service.get_download_url.return_value = "https://files.locker.io/signed"
        self.cipher_service = MagicMock()

    def _call(self, actions, method, url, data=None, user=None, pk=ACCESS_ID):
        view = QuickSharePwdViewSet.as_view(actions)
        request = getattr(self.factory, method)(url, data, format="json")
        if user:
            force_authenticate(request, user=user)
        with patch.object(QuickSharePwdViewSet, "quick_share_service", self.quick_share_service), \
                patch.object(QuickSharePwdViewSet, "attachment_service", self.attachment_service), \
                patch.object(QuickSharePwdViewSet, "cipher_service", self.cipher_service), \
                patch.object(QuickSharePwdViewSet, "get_throttles", return_value=[]):
            return view(request, pk=pk) if pk else view(request)

    def _attachment_url(self, data=None):
        return self._call(
            {"post": "attachment_url"}, "post", f"/v3/cystack_platform/pm/quick_shares/{ACCESS_ID}/attachments/url",
            data if data is not None else {"attachment_id": "a1", "attachment_token": "token"}
        )

    def test_anonymous_can_get_the_attachment_url(self):
        response = self._attachment_url()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"url": "https://files.locker.io/signed"})
        self.quick_share_service.get_attachment_path.assert_called_once_with(
            quick_share=self.quick_share, attachment_id="a1", attachment_token="token"
        )
        # The CDN urls are not signed, so the quick share urls never use the CDN
        self.attachment_service.get_download_url.assert_called_once_with(
            path=ATTACHMENT_KEY, is_cdn=False, expired=QUICK_SHARE_ATTACHMENT_URL_EXPIRED
        )
        self.quick_share_service.update_access_count.assert_not_called()

    def test_attachment_url_errors(self):
        self.quick_share_service.get_attachment_path.side_effect = QuickShareNotValidAccessException
        response = self._attachment_url()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "9000")

        self.quick_share_service.get_attachment_path.side_effect = QuickShareAttachmentNotValidException
        self.assertEqual(self._attachment_url().status_code, status.HTTP_404_NOT_FOUND)
        self.attachment_service.get_download_url.assert_not_called()

    def test_attachment_url_requires_the_fields(self):
        self.assertEqual(self._attachment_url(data={}).status_code, status.HTTP_400_BAD_REQUEST)
        self.quick_share_service.get_attachment_path.assert_not_called()

    def test_permission_allows_anonymous_attachment_url(self):
        view = MagicMock(action="attachment_url")
        self.assertTrue(QuickSharePwdPermission().has_permission(request=MagicMock(), view=view))

    def test_public_access_returns_the_attachment_token(self):
        self.quick_share_service.get_email_access.return_value = self.quick_share
        self.quick_share_service.issue_attachment_token.return_value = ("attachment-token", 123)
        response = self._call(
            {"get": "access"}, "get", f"/v3/cystack_platform/pm/quick_shares/{ACCESS_ID}/access"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["attachmentToken"], {"value": "attachment-token", "expiredTime": 123})
        self.quick_share_service.issue_attachment_token.assert_called_once_with(
            quick_share=self.quick_share, email=None
        )

    def test_public_returns_the_attachment_token_of_the_email(self):
        self.quick_share_service.public_quick_share.return_value = (self.quick_share, None, None)
        self.quick_share_service.issue_attachment_token.return_value = None
        response = self._call(
            {"post": "public"}, "post", f"/v3/cystack_platform/pm/quick_shares/{ACCESS_ID}/public",
            {"email": EMAIL, "code": "123456"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("attachmentToken", response.data)
        self.quick_share_service.issue_attachment_token.assert_called_once_with(
            quick_share=self.quick_share, email=EMAIL
        )

    def _create(self, side_effect):
        self.cipher_service.get_by_id.return_value = MagicMock(team=None, user=MagicMock(user_id=USER_ID))
        self.quick_share_service.create_user_quick_share.side_effect = side_effect
        user = User(user_id=USER_ID, email="user@example.com", activated=True)
        with patch.object(QuickSharePwdPermission, "has_permission", return_value=True), \
                patch.object(QuickSharePwdViewSet, "get_ip", return_value="127.0.0.1"):
            return self._call({"post": "create"}, "post", "/v3/cystack_platform/pm/quick_shares", {
                "cipher_id": CIPHER_ID, "key": "enc-key",
                "cipher": {"type": CIPHER_TYPE_LOGIN, "name": "enc", "notes": None, "login": {"username": "enc", "password": "enc", "totp": None, "uris": None},
                           "attachments": [attachment()]},
            }, user=user, pk=None)

    def test_create_with_invalid_attachments(self):
        response = self._create(QuickShareAttachmentNotValidException)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("attachments", response.data["details"]["cipher"])

    def test_create_when_the_user_can_not_view_the_cipher(self):
        self.assertEqual(self._create(CipherDoesNotExistException).status_code, status.HTTP_404_NOT_FOUND)

    def test_create_passes_the_attachments_to_the_service(self):
        response = self._create(lambda **kwargs: MagicMock(
            quick_share_id="qs-1", cipher=MagicMock(cipher_id=CIPHER_ID), access_id=ACCESS_ID
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        kwargs = self.quick_share_service.create_user_quick_share.call_args.kwargs
        self.assertEqual(kwargs["data"]["attachments"], [attachment()])
