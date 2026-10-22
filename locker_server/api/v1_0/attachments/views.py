from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.attachment_permission import AttachmentPwdPermission
from locker_server.api.v1_0.attachments.serializers import AttachmentUploadSerializer, SignedAttachmentSerializer, \
    MultipleDeleteAttachmentSerializer
from locker_server.core.exceptions.cipher_attachment_exception import CipherAttachmentLimitSizeReachedException
from locker_server.core.exceptions.cipher_exception import CipherDoesNotExistException
from locker_server.shared.constants.attachments import DEFAULT_ATTACHMENT_EXPIRED, UPLOAD_ACTION_ATTACHMENT
from locker_server.shared.constants.emergency_access import EMERGENCY_ACCESS_TYPE_VIEW, \
    EMERGENCY_ACCESS_STATUS_RECOVERY_APPROVED
from locker_server.shared.constants.transactions import PLAN_TYPE_PM_FREE
from locker_server.shared.error_responses.error import gen_error
from locker_server.shared.external_services.attachments.attachment_factory import ATTACHMENT_R2
from locker_server.shared.external_services.attachments.exceptions import FileExtensionNotAllowedException, \
    AttachmentCreateUploadFormException
from locker_server.shared.utils.attachments import parse_attachment_key


class AttachmentPwdViewSet(APIBaseViewSet):
    permission_classes = (AttachmentPwdPermission, )
    http_method_names = ["head", "options", "post", ]

    def get_throttles(self):
        throttles = super().get_throttles()
        self.throttle_scope = "attachments"
        return throttles

    def get_serializer_class(self):
        if self.action == "create":
            self.serializer_class = AttachmentUploadSerializer
        elif self.action in ["signed", "url"]:
            self.serializer_class = SignedAttachmentSerializer
        elif self.action == "multiple_delete":
            self.serializer_class = MultipleDeleteAttachmentSerializer
        return super().get_serializer_class()

    def allow_attachments(self) -> bool:
        user = self.request.user
        current_plan = self.user_service.get_current_plan(user=user)
        plan = current_plan.pm_plan
        is_active_enterprise_member = self.user_service.is_active_enterprise_member(user_id=user.user_id)
        return plan.alias not in [PLAN_TYPE_PM_FREE] or is_active_enterprise_member

    def get_cipher_obj(self, cipher_id: str):
        try:
            cipher = self.cipher_service.get_by_id(cipher_id=cipher_id)
            if cipher.team:
                self.check_object_permissions(request=self.request, obj=cipher)
            else:
                if cipher.user.user_id != self.request.user.user_id:
                    return None
            return cipher
        except CipherDoesNotExistException:
            return None

    def can_view_cipher_attachments(self, cipher_id: str) -> bool:
        """
        The user can view the attachments of a cipher if the user can view the cipher in the vault
        """
        user = self.request.user
        # The owner or the members of the sharing team (the same scope as the sync)
        if self.cipher_service.get_multiple_by_user(user_id=user.user_id, filter_ids=[cipher_id]):
            return True
        # The grantee of an approved view emergency access (the same scope as the emergency access view)
        for emergency_access in self.emergency_access_service.list_by_grantee_id(grantee_id=user.user_id):
            if emergency_access.emergency_access_type != EMERGENCY_ACCESS_TYPE_VIEW or \
                    emergency_access.status != EMERGENCY_ACCESS_STATUS_RECOVERY_APPROVED or \
                    not emergency_access.grantor:
                continue
            if self.cipher_service.get_multiple_by_user(
                user_id=emergency_access.grantor.user_id, filter_ids=[cipher_id]
            ):
                return True
        # The quick shares do not grant the access: the quick share data does not contain the attachments
        return False

    def create(self, request, *args, **kwargs):
        allow_upload_file = self.allow_attachments()
        if allow_upload_file is False:
            raise ValidationError({"non_field_errors": [gen_error("7002")]})

        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        upload_action = validated_data.get("action")
        file_name = validated_data.get("file_name")
        metadata = validated_data.get("metadata") or {}
        metadata.update({
            "user_key": self.user_service.get_hash_user_key(user=user),
        })
        # Validate data: Check permission
        limit_size = True

        if upload_action == UPLOAD_ACTION_ATTACHMENT:
            cipher_id = metadata.get("cipher_id")
            cipher = self.get_cipher_obj(cipher_id=cipher_id)
            if not cipher:
                raise PermissionDenied
        try:
            metadata.update({
                "limit": limit_size,
                "method": "put",
            })
            allocated_attachment = self.attachment_service.get_attachment_upload_form(
                action=upload_action, file_name=file_name, **metadata
            )
        except FileExtensionNotAllowedException:
            raise ValidationError(detail={"file_name": ["This file type is not valid"]})
        except AttachmentCreateUploadFormException:
            raise ValidationError({"non_field_errors": [gen_error("0009")]})
        except CipherAttachmentLimitSizeReachedException:
            raise ValidationError({"non_field_errors": [gen_error("5003")]})
        return Response(status=status.HTTP_200_OK, data=allocated_attachment)

    @action(methods=["post"], detail=False)
    def url(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        # Only sign the normalized key of an attachment which the user can view.
        # The invalid paths and the denied paths return the same error, so the cipher ids can not be enumerated
        attachment = parse_attachment_key(validated_data.get("path"))
        if not attachment:
            raise NotFound
        path, cipher_id = attachment
        if self.can_view_cipher_attachments(cipher_id=cipher_id) is False:
            raise NotFound
        if settings.DEFAULT_CLOUD_STORAGE == ATTACHMENT_R2 and settings.CDN_ATTACHMENT_URL:
            is_cdn = True
        elif settings.AWS_CLOUDFRONT_PUBLIC_KEY_ID:
            is_cdn = True
        else:
            is_cdn = False
        # The attachments are downloaded (and decrypted by the clients), they are never rendered by the browser
        onetime_url = self.attachment_service.get_onetime_url(path=path, is_cdn=is_cdn, **{
            "response_content_disposition": "attachment",
            "expired": DEFAULT_ATTACHMENT_EXPIRED
        })
        return Response(status=status.HTTP_200_OK, data={"url": onetime_url})

    @action(methods=["post"], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        paths = validated_data.get("paths", [])

        deleted_paths = []
        for attachment_path in paths:
            try:
                cipher_id = attachment_path.split("/")[2]
            except IndexError:
                raise ValidationError(detail={"paths": [f"The attachment path {attachment_path} does not exist"]})
            cipher = self.get_cipher_obj(cipher_id=cipher_id)
            if cipher:
                deleted_paths.append(attachment_path)
        self.attachment_service.delete_multiple_attachments(paths=deleted_paths)
        return Response(status=status.HTTP_200_OK, data={"success": True})


