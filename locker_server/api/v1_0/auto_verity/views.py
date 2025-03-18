from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.auto_verify_permission import AutoVerifyPwdPermission
from locker_server.api.v1_0.auto_verity.serializers import CreateAutoVerifySerializer, DeviceAutoVerifySerializer
from locker_server.core.exceptions.device_exception import DeviceDoesNotExistException
from locker_server.core.exceptions.user_exception import UserAuthFailedException


class AutoVerifyPwdViewSet(APIBaseViewSet):
    permission_classes = (AutoVerifyPwdPermission, )
    http_method_names = ["head", "options", "post"]

    def get_serializer_class(self):
        if self.action == "create":
            self.serializer_class = CreateAutoVerifySerializer
        elif self.action == "device_auto_verify":
            self.serializer_class = DeviceAutoVerifySerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request=request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            device = self.auto_verify_service.create_auto_verify(
                user_id=user.user_id, device_identifier=validated_data.get("device_id"),
                h=validated_data.get("h"), p=validated_data.get("p")
            )
        except DeviceDoesNotExistException:
            raise ValidationError(detail={"device_id": ["The device does not exist"]})
        return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(methods=["post"], detail=False)
    def device_auto_verify(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request=request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        try:
            result = self.auto_verify_service.get_auto_verify(
                user_id=user.user_id, device_identifier=validated_data.get("device_id"),
                ts=validated_data.get("ts"),
                s=validated_data.get("s"),
                pk=validated_data.get("pk"),
            )
            return Response(status=status.HTTP_200_OK, data=result)
        except DeviceDoesNotExistException:
            raise ValidationError(detail={"device_id": ["The device does not exist"]})
        except UserAuthFailedException:
            raise ValidationError(detail={"s": ["The signature is not valid"]})
