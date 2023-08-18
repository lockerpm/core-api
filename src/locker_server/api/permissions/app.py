from rest_framework.exceptions import PermissionDenied

from locker_server.shared.permissions.app import AppBasePermission


class APIPermission(AppBasePermission):
    def has_permission(self, request, view):
        return self.is_auth(request)

    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)
