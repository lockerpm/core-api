from rest_framework.exceptions import ValidationError

from locker_server.api.permissions.app import APIPermission
from locker_server.shared.error_responses.error import gen_error


class CipherPwdPermission(APIPermission):
    scope = 'cipher'

    def has_permission(self, request, view):
        is_authenticated = self.is_auth(request) and request.user.activated
        if not is_authenticated:
            return False
        if self.is_locked_by_enterprise(user=request.user):
            raise ValidationError({"non_field_errors": [gen_error("1009")]})
        return True

    def has_object_permission(self, request, view, obj):
        if view.action in ["update", "share"]:
            return self.can_edit_cipher(request, obj)
        if view.action in ["retrieve", "share_members", "cipher_use"]:
            return self.can_retrieve_cipher(request, obj)
        return False
