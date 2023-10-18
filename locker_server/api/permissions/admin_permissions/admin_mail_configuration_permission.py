from locker_server.api.permissions.app import APIPermission


class AdminMailConfigurationPermission(APIPermission):

    def has_permission(self, request, view):
        return self.is_auth(request) and self.is_admin(request)

    def has_object_permission(self, request, view, obj):
        return False