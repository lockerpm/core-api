import random

from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.passwordless_pwd_permission import PasswordlessPwdPermission
from locker_server.core.exceptions.user_exception import UserDoesNotExistException
from locker_server.shared.constants.backup_credential import WEBAUTHN_VALID_TRANSPORTS
from .serializers import PasswordlessCredentialSerializer


class PasswordlessPwdViewSet(APIBaseViewSet):
    permission_classes = (PasswordlessPwdPermission,)
    http_method_names = ["head", "options", "get", "post", "delete"]

    def get_serializer_class(self):
        if self.action == "credential":
            self.serializer_class = PasswordlessCredentialSerializer
        return super().get_serializer_class()

    @action(methods=["get", "post", "delete"], detail=False)
    def credential(self, request, *args, **kwargs):
        user = self.request.user
        if request.method == "GET":
            user_backup_credentials_data = []
            if not user or isinstance(user, AnonymousUser):
                email = self.request.query_params.get("email")
                if not email:
                    raise NotFound
                try:
                    user = self.user_service.retrieve_by_email(email=email)
                except UserDoesNotExistException:
                    raise NotFound
            user_backup_credentials = self.backup_credential_service.list_backup_credentials(**{
                "user_id": user.user_id
            })
            for backup_credential in user_backup_credentials:
                user_backup_credentials_data.append({
                    "credential_id": backup_credential.fd_credential_id,
                    "random": backup_credential.fd_random,
                    "transports": backup_credential.fd_transports or WEBAUTHN_VALID_TRANSPORTS,
                    "name": backup_credential.name,
                    "type": backup_credential.type,
                    "creation_date": backup_credential.creation_date,
                    "last_use_date": backup_credential.last_use_date,
                })
            return Response(status=status.HTTP_200_OK, data={
                "credential_id": user.fd_credential_id,
                "random": user.fd_random,
                "transports": user.fd_transports or WEBAUTHN_VALID_TRANSPORTS,
                "name": user.fd_name,
                "type": user.fd_type,
                "creation_date": user.fd_creation_date,
                "last_use_date": user.fd_last_use_date,
                "backup_keys": user_backup_credentials_data
            })

        elif request.method == "POST":
            # Saving the cred id of the user
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data
            credential_id = validated_data.get("credential_id")
            name = validated_data.get("name")
            fd_type = validated_data.get("type")
            credential_random = validated_data.get("random") or random.randbytes(16).hex()
            transports = validated_data.get("transports")
            user = self.user_service.update_passwordless_cred(
                user=user, fd_credential_id=credential_id, fd_random=credential_random,
                fd_transports=transports,
                fd_name=name,
                fd_type=fd_type
            )
            return Response(status=status.HTTP_200_OK, data={
                "credential_id": user.fd_credential_id,
                "random": user.fd_random,
                "type": user.fd_type
            })
        elif request.method == "DELETE":
            user = self.user_service.delete_passwordless_cred(
                user=user
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
