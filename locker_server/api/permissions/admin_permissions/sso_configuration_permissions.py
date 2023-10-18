from locker_server.api.permissions.app import APIPermission
from locker_server.containers.containers import user_service


class SSOConfigurationPermission(APIPermission):
    def has_permission(self, request, view):
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        # TODO: check permission
        if view.action in ["sso_configuration", "update_sso_configuration", "destroy_sso_configuration"]:
            return obj.created_by.user_id == request.user.user_id
        return request.user