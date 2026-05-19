from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings
from rest_framework import status
from rest_framework.test import APIRequestFactory

from locker_server.api.v1_0.users.views import UserPwdViewSet
from locker_server.core.entities.factor2.factor2_method import Factor2Method
from locker_server.core.entities.user.user import User
from locker_server.core.exceptions.device_exception import DeviceDoesNotExistException
from locker_server.core.exceptions.user_exception import UserAuthFailedException
from locker_server.shared.constants.factor2 import FA2_METHOD_MAIL_OTP


@override_settings(SELF_HOSTED=True, SECRET_KEY="test-secret")
class UserSession2FATestCase(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User(
            user_id=1,
            email="user@example.com",
            is_factor2=True,
            activated=True,
        )
        self.request_data = {
            "email": "user@example.com",
            "password": "master-password",
            "client_id": "web",
            "device_identifier": "device-1",
        }

    def _post_session(self, user_service, device_service, factor2_service):
        view = UserPwdViewSet.as_view({"post": "session"})
        request = self.factory.post("/v3/cystack_platform/pm/users/session", self.request_data, format="json")
        with patch.object(UserPwdViewSet, "user_service", user_service), \
                patch.object(UserPwdViewSet, "device_service", device_service), \
                patch.object(UserPwdViewSet, "factor2_service", factor2_service):
            return view(request)

    def test_2fa_session_wrong_password_does_not_return_methods(self):
        user_service = MagicMock()
        user_service.retrieve_by_email.return_value = self.user
        user_service.check_user_session_auth.side_effect = UserAuthFailedException
        device_service = MagicMock()
        device_service.get_device_factor2_by_device_identifier.side_effect = DeviceDoesNotExistException
        factor2_service = MagicMock()

        response = self._post_session(user_service, device_service, factor2_service)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["details"]["password"][0], "Password is not correct")
        self.assertNotIn("methods", response.data)
        factor2_service.list_user_factor2_methods.assert_not_called()

    def test_2fa_session_correct_password_returns_active_methods(self):
        user_service = MagicMock()
        user_service.retrieve_by_email.return_value = self.user
        user_service.check_user_session_auth.return_value = ([], [], True)
        device_service = MagicMock()
        device_service.get_device_factor2_by_device_identifier.side_effect = DeviceDoesNotExistException
        factor2_service = MagicMock()
        factor2_service.list_user_factor2_methods.return_value = [
            Factor2Method(
                factor2_method_id=1,
                method=FA2_METHOD_MAIL_OTP,
                is_activate=True,
                activate_code="",
                code_expired_time=0,
                updated_time=0,
                user=self.user,
            )
        ]

        response = self._post_session(user_service, device_service, factor2_service)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {"is_factor2": True, "methods": [{"method": FA2_METHOD_MAIL_OTP, "is_active": True}]},
        )
        user_service.user_session.assert_not_called()

    def test_2fa_session_whitelisted_device_uses_full_session(self):
        user_service = MagicMock()
        user_service.retrieve_by_email.return_value = self.user
        user_service.user_session.return_value = {
            "access_token": "access-token",
            "refresh_token": "refresh-token",
            "token_type": "Bearer",
        }
        device_service = MagicMock()
        device_service.get_device_factor2_by_device_identifier.return_value = object()
        factor2_service = MagicMock()

        response = self._post_session(user_service, device_service, factor2_service)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["access_token"], "access-token")
        user_service.check_user_session_auth.assert_not_called()
        factor2_service.list_user_factor2_methods.assert_not_called()
