from rest_framework.exceptions import ValidationError

from locker_server.api.permissions.app import APIPermission
from locker_server.shared.error_responses.error import gen_error


class QuickSharePwdPermission(APIPermission):
    # scope = 'quick_share'

    def has_permission(self, request, view):
        if view.action in ["public", "access", "otp"]:
            return True
        is_authenticated = self.is_auth(request) and request.user.activated
        if not is_authenticated:
            return False
        if self.is_locked_by_enterprise(user=request.user):
            raise ValidationError({"non_field_errors": [gen_error("1009")]})
        return True

    def has_object_permission(self, request, view, obj):
        return obj.created_by and obj.created_by.user_id == request.user.user_id

    # def get_role_pattern(self, view):
    #     return super().get_role_pattern(view)
