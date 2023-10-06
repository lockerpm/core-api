from locker_server.api.permissions.app import APIPermission


class UserPwdPermission(APIPermission):
    def has_permission(self, request, view):
        if view.action in ["password_hint", "invitation_confirmation", "delete_multiple"]:
            return True
        if view.action in ["prelogin", "me", "session", "passwordless_require", "onboarding_process",
                           "block_by_2fa_policy", "login_method_me", "check_password"]:
            return self.is_auth(request)
        elif view.action in ["register"]:
            return self.is_auth(request) and request.user.activated is False
        elif view.action in ["retrieve", "dashboard", "list_users", "list_user_ids", "destroy"]:
            return self.is_admin(request)
        return self.is_auth(request) and request.user.activated
    
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)
