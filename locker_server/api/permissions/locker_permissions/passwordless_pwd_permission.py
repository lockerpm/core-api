from locker_server.api.permissions.app import APIPermission


class PasswordlessPwdPermission(APIPermission):
    def has_permission(self, request, view):
        return self.is_auth(request)

    def has_object_permission(self, request, view, obj):
        return super(PasswordlessPwdPermission, self).has_object_permission(request, view, obj)
