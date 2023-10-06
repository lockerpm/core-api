import random

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.passwordless_pwd_permission import PasswordlessPwdPermission
from .serializers import PasswordlessCredentialSerializer


class PasswordlessPwdViewSet(APIBaseViewSet):
    permission_classes = (PasswordlessPwdPermission, )
    http_method_names = ["head", "options", "get", "post", ]

    def get_serializer_class(self):
        if self.action == "credential":
            self.serializer_class = PasswordlessCredentialSerializer
        return super().get_serializer_class()

    @action(methods=["get", "post"], detail=False)
    def credential(self, request, *args, **kwargs):
        user = self.request.user
        if request.method == "GET":
            return Response(status=status.HTTP_200_OK, data={
                "credential_id": user.fd_credential_id,
                "random": user.fd_random
            })

        elif request.method == "POST":
            # Saving the cred id of the user
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data
            credential_id = validated_data.get("credential_id")
            credential_random = random.randbytes(16).hex()
            user = self.user_service.update_passwordless_cred(
                user=user, fd_credential_id=credential_id, fd_random=credential_random
            )
            return Response(status=status.HTTP_200_OK, data={
                "credential_id": user.fd_credential_id,
                "random": user.fd_random
            })
