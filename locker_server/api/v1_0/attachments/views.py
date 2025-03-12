from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.attachment_permission import AttachmentPwdPermission
from locker_server.api.v1_0.attachments.serializers import AttachmentUploadSerializer, SignedAttachmentSerializeR
from locker_server.core.exceptions.cipher_attachment_repository import CipherAttachmentDoesNotExistException
from locker_server.shared.constants.attachments import DEFAULT_ATTACHMENT_EXPIRED
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
            self.serializer_class = SignedAttachmentSerializeR
        return super().get_serializer_class()

    def get_cipher_attachment_by_path(self, path: str):
        try:
            cipher_attachment = self.attachment_service.get_cipher_attachment_by_path(path=path)
        except CipherAttachmentDoesNotExistException:
            return None
        self.check_object_permissions(request=self.request, obj=cipher_attachment)
        return cipher_attachment

    def create(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        upload_action = validated_data.get("action")
        file_name = validated_data.get("file_name")
        metadata = validated_data.get("metadata") or {}
        metadata.update({
            "user_key": self.user_service.get_hash_user_key(user=user)
        })
        # Update content type
        attachment_storage = AttachmentStorageFactory.get_attachment_service(service_name=ATTACHMENT_AWS)
        extension = attachment_storage.get_file_name(file_path=file_name)[1]
        if extension.lower() in [".jpg", ".png", ".jpeg"]:
            metadata.update({"content_type": 'image/jpeg'})
        # Validate data: Check permission
        limit_size = True
        try:
            metadata.update({"limit": limit_size})
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
        onetime_url = self.attachment_service.get_onetime_url(path=path, is_cdn=True, **{
            "response_content_disposition": "inline",
            "expired": DEFAULT_ATTACHMENT_EXPIRED
        })
        return Response(status=status.HTTP_200_OK, data={"url": onetime_url})
