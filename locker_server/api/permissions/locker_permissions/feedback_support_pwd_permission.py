from locker_server.api.permissions.app import APIPermission


class FeedbackSupportPwdPermission(APIPermission):
    def has_permission(self, request, view):
        if view.action in ["report"]:
            return True
        return self.is_auth(request)

    def has_object_permission(self, request, view, obj):
        return False
