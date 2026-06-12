from django.conf import settings

from locker_server.api.permissions.app import APIPermission


class UserPwdPermission(APIPermission):
    def has_permission(self, request, view):
        if view.action in ["invitation_confirmation", "clear_cache", "delete_multiple"]:
            auth_header = request.META.get("HTTP_AUTHORIZATION")
            try:
                auth_token = auth_header.split()[1]
                return auth_token == settings.MANAGEMENT_COMMAND_TOKEN
            except (AttributeError, IndexError):
                return False

        elif view.action in ["password_hint", "session", "session_by_otp", "check_password", "exist",
                             "prelogin", "reset_password", "access_token"]:
            return True
        elif view.action in ["me", "passwordless_require", "onboarding_process",
                             "block_by_2fa_policy", "login_method_me", "prelogin_me"]:
            return self.is_auth(request)
        elif view.action in ["register"]:
            return self.is_auth(request) is False or request.user.activated is False
        elif view.action in ["retrieve", "dashboard", "list_users", "list_user_ids", "destroy"]:
            return self.is_admin(request)
        return self.is_auth(request) and request.user.activated

    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)
