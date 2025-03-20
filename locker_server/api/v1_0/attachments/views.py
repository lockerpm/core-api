from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.attachment_permission import AttachmentPwdPermission
from locker_server.api.v1_0.attachments.serializers import AttachmentUploadSerializer, SignedAttachmentSerializer, \
    MultipleDeleteAttachmentSerializer
from locker_server.core.exceptions.cipher_attachment_exception import CipherAttachmentDoesNotExistException
from locker_server.core.exceptions.cipher_exception import CipherDoesNotExistException
from locker_server.shared.constants.attachments import DEFAULT_ATTACHMENT_EXPIRED, UPLOAD_ACTION_ATTACHMENT
from locker_server.shared.constants.transactions import PLAN_TYPE_PM_FREE
from locker_server.shared.error_responses.error import gen_error
from locker_server.shared.external_services.attachments.attachment_factory import AttachmentStorageFactory, \
    ATTACHMENT_AWS
from locker_server.shared.external_services.attachments.exceptions import FileExtensionNotAllowedException, \
    AttachmentCreateUploadFormException


class AttachmentPwdViewSet(APIBaseViewSet):
    permission_classes = (AttachmentPwdPermission, )
    http_method_names = ["head", "options", "post", ]

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

    def get_cipher_attachment_by_path(self, path: str):
        try:
            cipher_attachment = self.attachment_service.get_cipher_attachment_by_path(path=path)
        except CipherAttachmentDoesNotExistException:
            return None
        self.check_object_permissions(request=self.request, obj=cipher_attachment)
        return cipher_attachment

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
        # Update content type
        attachment_storage = AttachmentStorageFactory.get_attachment_service(
            service_name=settings.DEFAULT_CLOUD_STORAGE
        )
        extension = attachment_storage.get_file_name(file_path=file_name)[1]
        if extension.lower() in [".jpg", ".png", ".jpeg"]:
            metadata.update({"content_type": 'image/jpeg'})
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
        return Response(status=status.HTTP_200_OK, data=allocated_attachment)

    @action(methods=["post"], detail=False)
    def url(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        path = validated_data.get("path")
        is_cdn = True if settings.AWS_CLOUDFRONT_PUBLIC_KEY_ID else False
        onetime_url = self.attachment_service.get_onetime_url(path=path, is_cdn=is_cdn, **{
            "response_content_disposition": "inline",
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


