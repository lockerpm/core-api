from rest_framework.exceptions import PermissionDenied

from locker_server.api.permissions.app import APIPermission
from locker_server.core.exceptions.enterprise_member_exception import EnterpriseMemberDoesNotExistException
from locker_server.shared.constants.enterprise_members import E_MEMBER_ROLE_PRIMARY_ADMIN, E_MEMBER_ROLE_ADMIN
from locker_server.containers.containers import enterprise_member_service


class EnterprisePwdPermission(APIPermission):
    scope = 'enterprise'

    def has_permission(self, request, view):
        return self.is_auth(request)

    def has_object_permission(self, request, view, obj):
        if view.action in ["dashboard"]:
            member = self.get_enterprise_member(user=request.user, obj=obj)
            role = member.role
            role_name = role.name
            return role_name in [E_MEMBER_ROLE_PRIMARY_ADMIN, E_MEMBER_ROLE_ADMIN]
        return super().has_object_permission(request, view, obj)

    @staticmethod
    def get_enterprise_member(user, obj):
        try:
            enterprise_member = enterprise_member_service.get_member_by_user(
                user_id=user.user_id,
                enterprise_id=obj.enterprise_id
            )
            return enterprise_member
        except EnterpriseMemberDoesNotExistException:
            raise PermissionDenied