from locker_server.api.permissions.app import APIPermission
from locker_server.containers.containers import user_service


class SSOConfigurationPermission(APIPermission):
    def has_permission(self, request, view):
        if view.action in ["get_sso_config", "get_user_from_sso"]:
            return True
        # TODO: check permission view.action in ["create"]
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if view.action in ["update", "destroy"]:
            return obj.created_by.user_id == request.user.user_id
        return request.user
