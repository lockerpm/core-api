from locker_server.api.permissions.admin_permissions.admin_enterprise_permission import AdminEnterprisePermission
from locker_server.shared.constants.enterprise_members import E_MEMBER_ROLE_PRIMARY_ADMIN


class AdminEnterpriseMemberPermission(AdminEnterprisePermission):

    def has_permission(self, request, view):
        return self.is_auth(request) and request.user.is_supper_admin

    def has_object_permission(self, request, view, obj):
        member = self.get_enterprise_member(user=request.user, obj=obj)
        role = member.role
        role_name = role.name
        if view.action in ["list", "retrieve", "update", "activated", "destroy"]:
            return role_name in [E_MEMBER_ROLE_PRIMARY_ADMIN]
        return super().has_object_permission(request, view, obj)
