from locker_server.api.permissions.admin_permissions.admin_enterprise_permission import AdminEnterprisePermission


class AdminAppInfoPermission(AdminEnterprisePermission):

    def has_permission(self, request, view):
        return self.is_auth(request) and request.user.is_super_admin

    def has_object_permission(self, request, view, obj):
        if view.action in ["app_info_logo", "update_app_info"]:
            if request.method == "PUT":
                return request.user.is_super_admin
        return super().has_object_permission(request, view, obj)
