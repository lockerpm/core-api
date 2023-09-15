from locker_server.api.permissions.app import APIPermission


class SyncPwdPermission(APIPermission):
    # scope = 'folder'

    def has_permission(self, request, view):
        return self.is_auth(request) and request.user.activated

    def has_object_permission(self, request, view, obj):
        if view.action == "sync_cipher_detail":
            return self.can_retrieve_cipher(request, obj)

        return super(SyncPwdPermission, self).has_object_permission(request, view, obj)
