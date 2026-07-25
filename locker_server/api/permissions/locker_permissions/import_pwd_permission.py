from rest_framework.exceptions import ValidationError

from locker_server.api.permissions.app import APIPermission
from locker_server.shared.error_responses.error import gen_error


class ImportPwdPermission(APIPermission):
    scope = 'import_data'

    def has_permission(self, request, view):
        is_authenticated = self.is_auth(request) and request.user.activated
        if not is_authenticated:
            return False
        if self.is_locked_by_enterprise(user=request.user):
            raise ValidationError({"non_field_errors": [gen_error("1009")]})
        return True

    def has_object_permission(self, request, view, obj):
        """

        :param request:
        :param view:
        :param obj:
        :return:
        """
        return super(ImportPwdPermission, self).has_object_permission(request, view, obj)

