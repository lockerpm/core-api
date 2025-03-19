from locker_server.api.permissions.app import APIPermission
from locker_server.shared.constants.attachments import UPLOAD_ACTION_ATTACHMENT


class AttachmentPwdPermission(APIPermission):
    scope = 'attachment'

    def has_permission(self, request, view):
        return self.is_auth(request) and request.user.activated

    def has_object_permission(self, request, view, obj):

        if view.action == "create":
            upload_action = request.data.get("action")
            if upload_action == UPLOAD_ACTION_ATTACHMENT:
                return self.can_edit_cipher(request, obj)
        elif view.action == "multiple_delete":
            return self.can_edit_cipher(request, obj)

        return False
