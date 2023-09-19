import json

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError, AuthenticationFailed
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.sharing_pwd_permission import SharingPwdPermission
from locker_server.core.exceptions.cipher_exception import FolderDoesNotExistException, CipherMaximumReachedException
from locker_server.core.exceptions.collection_exception import CollectionDoesNotExistException, \
    CollectionCannotRemoveException, CollectionCannotAddException
from locker_server.core.exceptions.device_exception import DeviceDoesNotExistException
from locker_server.core.exceptions.team_exception import TeamDoesNotExistException, TeamLockedException
from locker_server.core.exceptions.team_member_exception import TeamMemberDoesNotExistException, \
    OnlyAllowOwnerUpdateException, OwnerDoesNotExistException
from locker_server.core.exceptions.user_exception import UserDoesNotExistException, \
    UserAuthBlockingEnterprisePolicyException, UserAuthFailedException, UserAuthBlockedEnterprisePolicyException, \
    UserIsLockedByEnterpriseException, UserEnterprisePlanExpiredException, UserBelongEnterpriseException, \
    User2FARequireException, UserAuthFailedPasswordlessRequiredException
from locker_server.shared.constants.account import *
from locker_server.shared.error_responses.error import refer_error, gen_error
from locker_server.api.v1_0.ciphers.serializers import VaultItemSerializer, UpdateVaultItemSerializer
from locker_server.shared.external_services.pm_sync import PwdSync, SYNC_EVENT_CIPHER_UPDATE
from .serializers import UserPublicKeySerializer, SharingInvitationSerializer


class SharingPwdViewSet(APIBaseViewSet):
    permission_classes = (SharingPwdPermission,)
    http_method_names = ["head", "options", "get", "post", "put"]
    lookup_value_regex = r'[0-9a-z-]+'

    def get_throttles(self):
        return super().get_throttles()

    def get_serializer_class(self):
        if self.action == "public_key":
            self.serializer_class = UserPublicKeySerializer
        elif self.action == "invitations":
            self.serializer_class = SharingInvitationSerializer

        return super().get_serializer_class()

    def allow_personal_sharing(self, user):
        user = self.request.user
        current_plan = self.user_service.get_current_plan(user=user)
        plan = current_plan.pm_plan
        is_active_enterprise_member = self.user_service.is_active_enterprise_member(user_id=user.user_id)
        if not (plan.personal_share or is_active_enterprise_member):
            raise ValidationError({"non_field_errors": [gen_error("7002")]})
        return user

    def get_personal_share(self, sharing_id):
        try:
            team = self.sharing_service.get_by_id(sharing_id=sharing_id)
            if team.personal_share is False:
                raise NotFound
            self.check_object_permissions(request=self.request, obj=team)
            return team
        except TeamDoesNotExistException:
            raise NotFound

    @action(methods=["post"], detail=False)
    def public_key(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user_id = validated_data.get("user_id")
        try:
            user_obj = self.user_service.retrieve_by_id(user_id=user_id)
            if not user_obj.activated:
                return Response(status=status.HTTP_200_OK, data={"public_key": None})
        except UserDoesNotExistException:
            return Response(status=status.HTTP_200_OK, data={"public_key": None})
        return Response(status=status.HTTP_200_OK, data={"public_key": user_obj.public_key})

    @action(methods=["get"], detail=False)
    def invitations(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request=request)
        sharing_invitations = self.sharing_service.list_sharing_invitations(user_id=user.user_id)
        serializer = self.get_serializer(sharing_invitations, many=True)
        sharing_invitations = serializer.data
        for sharing_invitation in sharing_invitations:
            sharing_id = sharing_invitation.get("team").get("id")
            try:
                owner_user_id = self.sharing_service.get_sharing_owner(sharing_id=sharing_id).user.user_id
            except OwnerDoesNotExistException:
                owner_user_id = None
            item_type = "folder" if self.sharing_service.is_folder_sharing(sharing_id=sharing_id) else "cipher"
            cipher_type = self.sharing_service.get_sharing_cipher_type(sharing_id=sharing_id)
            sharing_invitation["owner"] = owner_user_id
            sharing_invitation["item_type"] = item_type
            sharing_invitation["share_type"] = self.sharing_service.get_personal_share_type(
                role=sharing_invitation["role"]
            )
            sharing_invitation["cipher_type"] = cipher_type

        return Response(status=status.HTTP_200_OK, data=sharing_invitations)
