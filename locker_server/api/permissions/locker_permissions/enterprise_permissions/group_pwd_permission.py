from rest_framework.permissions import SAFE_METHODS

from locker_server.api.permissions.locker_permissions.enterprise_permissions.enterprise_pwd_permission import \
    EnterprisePwdPermission
from locker_server.shared.constants.enterprise_members import E_MEMBER_ROLE_PRIMARY_ADMIN, E_MEMBER_ROLE_ADMIN, \
    E_MEMBER_ROLE_MEMBER


class GroupPwdPermission(EnterprisePwdPermission):
    scope = 'group'

    def has_permission(self, request, view):
        return self.is_auth(request)

    def has_object_permission(self, request, view, obj):
        if self.is_super_admin(request):
            return True
        member = self.get_enterprise_member(user=request.user, obj=obj)
        role = member.role
        role_name = role.name
        # Write actions (members PUT, create/update/destroy) require an active, confirmed member:
        # a deactivated or still-pending admin must not be able to change group membership or
        # silently grant/revoke shared-vault access.
        if request.method not in SAFE_METHODS and not self.is_activated_member(member):
            return False
        if view.action in ["members_list"]:
            return role_name in [E_MEMBER_ROLE_PRIMARY_ADMIN, E_MEMBER_ROLE_ADMIN, E_MEMBER_ROLE_MEMBER]
        return role_name in [E_MEMBER_ROLE_PRIMARY_ADMIN, E_MEMBER_ROLE_ADMIN]
