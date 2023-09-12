from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.exclude_domain_pwd_permission import ExcludeDomainPwdPermission
from locker_server.api.permissions.locker_permissions.folder_pwd_permission import FolderPwdPermission
from locker_server.core.exceptions.cipher_exception import FolderDoesNotExistException
from locker_server.core.exceptions.exclude_domain_exception import ExcludeDomainNotExistException
from locker_server.shared.external_services.pm_sync import SYNC_EVENT_FOLDER_UPDATE, PwdSync, SYNC_EVENT_FOLDER_DELETE
from locker_server.shared.utils.app import camel_snake_data
from .serializers import FolderSerializer, DetailFolderSerializer


class FolderPwdViewSet(APIBaseViewSet):
    permission_classes = (FolderPwdPermission, )
    http_method_names = ["head", "options", "get", "post", "put", "delete"]
    serializer_class = FolderSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            self.serializer_class = DetailFolderSerializer
        return super().get_serializer_class()

    def get_object(self):
        try:
            folder = self.folder_service.get_by_id(folder_id=self.kwargs.get("pk"))
            if folder.user.user_id != self.request.user.user_id:
                raise NotFound
            return folder
        except FolderDoesNotExistException:
            raise NotFound

    def create(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request=request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        name = validated_data.get("name")

        # We create new folder object from folder data
        # Then we update revision date of user
        new_folder = self.folder_service.create_new_folder(user_id=user.user_id, name=name)
        self.user_service.delete_sync_cache_data(user_id=user.user_id)
        PwdSync(event=SYNC_EVENT_FOLDER_UPDATE, user_ids=[user.user_id]).send(data={"id": str(new_folder.folder_id)})
        return Response(status=200, data={"id": new_folder.id})

    def retrieve(self, request, *args, **kwargs):
        self.check_pwd_session_auth(request=request)
        folder = self.get_object()
        serializer = self.get_serializer(folder)
        result = camel_snake_data(serializer.data, snake_to_camel=True)
        return Response(status=200, data=result)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request=request)
        folder = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        name = validated_data.get("name", folder.name)

        folder = self.folder_service.update_folder(user_id=user.user_id, folder_id=folder.folder_id, name=name)
        self.user_service.delete_sync_cache_data(user_id=user.user_id)
        PwdSync(event=SYNC_EVENT_FOLDER_UPDATE, user_ids=[user.user_id]).send(data={"id": str(folder.id)})
        return Response(status=200, data={"id": folder.id})

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request=request)
        folder = self.get_object()
        folder_id = kwargs.get("pk")
        user_id = user.user_id
        # Get list cipher of this folder then re-set folder of cipher
        ciphers = self.cipher_repository.get_multiple_by_user(user=user)
        soft_delete_cipher = []
        for cipher in ciphers:
            folders_dict = cipher.get_folders()
            cipher_folder_id = folders_dict.get(user_id, None)
            if cipher_folder_id == folder_id:
                folders_dict[user_id] = None
                cipher.folders = folders_dict
                cipher.save()
                if not cipher.team_id:
                    soft_delete_cipher.append(cipher.id)
        # Soft delete all ciphers in folder
        self.cipher_repository.delete_multiple_cipher(cipher_ids=soft_delete_cipher, user_deleted=user)
        # Delete this folder object
        folder.delete()


        # Clear sync data
        self.user_service.delete_sync_cache_data(user_id=user.user_id)
        # Sending sync event
        PwdSync(event=SYNC_EVENT_FOLDER_DELETE, user_ids=[user.user_id]).send()
        return Response(status=204)
