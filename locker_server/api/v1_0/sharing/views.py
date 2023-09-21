from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.sharing_pwd_permission import SharingPwdPermission
from locker_server.core.exceptions.cipher_exception import *
from locker_server.core.exceptions.collection_exception import *
from locker_server.core.exceptions.enterprise_group_exception import *
from locker_server.core.exceptions.team_exception import *
from locker_server.core.exceptions.team_member_exception import *
from locker_server.core.exceptions.user_exception import UserDoesNotExistException
from locker_server.shared.constants.members import PM_MEMBER_STATUS_INVITED, PM_MEMBER_STATUS_ACCEPTED
from locker_server.shared.error_responses.error import gen_error
from .serializers import UserPublicKeySerializer, SharingInvitationSerializer, SharingSerializer, \
    MultipleSharingSerializer, UpdateInvitationRoleSerializer, GroupMemberConfirmSerializer, \
    UpdateGroupInvitationRoleSerializer, StopSharingSerializer, AddMemberSerializer, UpdateShareFolderSerializer, \
    StopSharingFolderSerializer, AddItemShareFolderSerializer


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
        elif self.action == "share":
            self.serializer_class = SharingSerializer
        elif self.action == "multiple_share":
            self.serializer_class = MultipleSharingSerializer
        elif self.action == "update_role":
            self.serializer_class = UpdateInvitationRoleSerializer
        elif self.action == "invitation_group_confirm":
            self.serializer_class = GroupMemberConfirmSerializer
        elif self.action == "update_group_role":
            self.serializer_class = UpdateGroupInvitationRoleSerializer
        elif self.action in ["stop_share", "stop_group_share", "stop_share_cipher_folder"]:
            self.serializer_class = StopSharingSerializer
        elif self.action == "add_member":
            self.serializer_class = AddMemberSerializer
        elif self.action == "update_share_folder":
            self.serializer_class = UpdateShareFolderSerializer
        elif self.action in ["stop_share_folder", "delete_share_folder"]:
            self.serializer_class = StopSharingFolderSerializer
        elif self.action in ["add_item_share_folder", "remove_item_share_folder"]:
            self.serializer_class = AddItemShareFolderSerializer

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

    @action(methods=["put"], detail=False)
    def invitation_update(self, request, *args, **kwargs):
        self.check_pwd_session_auth(request=request)
        user = self.request.user
        invitation_status = request.data.get("status")
        if invitation_status not in ["accept", "reject"]:
            raise ValidationError(detail={"status": ["This status is not valid"]})
        try:
            sharing_invitation = self.sharing_service.get_shared_member(sharing_member_id=kwargs.get("pk"))
            if sharing_invitation.status != PM_MEMBER_STATUS_INVITED or sharing_invitation.team.key is None or \
                    sharing_invitation.user.activated is False:
                raise NotFound

        except TeamMemberDoesNotExistException:
            raise NotFound

        result = self.sharing_service.update_sharing_invitation(sharing_invitation=sharing_invitation, status=status)
        self._notify_invitation_update(data=result)
        return Response(status=status.HTTP_200_OK, data=result)

    @staticmethod
    def _notify_invitation_update(data):
        # TODO: Sending mail here
        # status = res_data.get("status")
        # member_status = res_data.get("member_status")
        # notification_user_ids = res_data.get("notification_user_ids") or []
        # mail_user_ids = res_data.get("mail_user_ids") or []
        #
        # # Sending notification and mail
        # if status == "accept":
        #     job = PWD_CONFIRM_SHARE_ITEM if member_status == "accepted" else PWD_SHARE_ITEM_ACCEPTED
        # else:
        #     job = PWD_SHARE_ITEM_REJECTED
        #
        # LockerBackgroundFactory.get_background(bg_name=BG_NOTIFY).run(
        #     func_name="notify_sending", **{
        #         "user_ids": mail_user_ids,
        #         "job": job,
        #         "name": user.full_name,
        #         "recipient_name": user.full_name,
        #
        #     }
        # )
        # LockerBackgroundFactory.get_background(bg_name=BG_NOTIFY).run(
        #     func_name="notify_sending", **{
        #         "services": [SENDING_SERVICE_WEB_NOTIFICATION],
        #         "user_ids": notification_user_ids,
        #         "job": job,
        #         "name": user.full_name,
        #         "recipient_name": user.full_name,
        #
        #     }
        # )
        pass

    @action(methods=["put"], detail=False)
    def share(self, request, *args, **kwargs):
        ip = self.get_ip()
        user = self.request.user
        self.check_pwd_session_auth(request)
        self.allow_personal_sharing(user=user)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()
        sharing_key = validated_data.get("sharing_key")
        members = validated_data.get("members")
        groups = validated_data.get("groups") or []
        cipher = validated_data.get("cipher")
        shared_cipher_data = validated_data.get("shared_cipher_data")
        folder = validated_data.get("folder")

        try:
            owner_name = user.full_name
        except AttributeError:
            owner_name = request.data.get("owner_name")

        try:
            result = self.sharing_service.share_cipher_or_folder(
                user=user, sharing_key=sharing_key, members=members, groups=groups,
                cipher=cipher, shared_cipher_data=shared_cipher_data, folder=folder,
                owner_name=owner_name, ip=ip
            )
        except EnterpriseGroupDoesNotExistException:
            raise ValidationError(detail={"groups": {"id": ["The group id does not exist"]}})
        except TeamMemberDoesNotExistException:
            raise ValidationError(detail={"groups": {"members": ["The member user id is not valid"]}})
        except TeamMemberEmailDoesNotExistException:
            raise ValidationError(detail={"groups": {"members": ["The member emails are not valid"]}})
        except CipherBelongCollectionException:
            raise ValidationError(detail={"cipher": ["The cipher does not exist"]})
        except FolderDoesNotExistException:
            raise ValidationError(detail={"folder": ["The folder does not exist"]})
        except CipherBelongTeamException:
            raise ValidationError({"non_field_errors": [gen_error("5000")]})

        new_sharing = result.get("new_sharing")
        return Response(status=200, data={
            "id": str(new_sharing.id),
            "shared_type_name": result.get("shared_type_name"),
            "folder_id": result.get("folder_id"),
            "cipher_id": result.get("cipher_id"),
            "non_existed_member_users": result.get("non_existed_member_users"),
            "mail_user_ids": result.get("mail_user_ids"),
            "notification_user_ids": result.get("notification_user_ids"),
        })

    @action(methods=["put"], detail=False)
    def multiple_share(self, request, *args, **kwargs):
        ip = self.get_ip()
        user = self.request.user
        try:
            owner_name = user.full_name
        except AttributeError:
            owner_name = request.data.get("owner_name")
        self.check_pwd_session_auth(request)
        self.allow_personal_sharing(user=user)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()
        sharing_key = validated_data.get("sharing_key")
        ciphers = validated_data.get("ciphers")
        folders = validated_data.get("folders")

        try:
            result = self.sharing_service.share_multiple_ciphers_or_folders(
                user=user, sharing_key=sharing_key, ciphers=ciphers, folders=folders,
                owner_name=owner_name, ip=ip
            )
        except EnterpriseGroupDoesNotExistException:
            raise ValidationError(detail={"group": {"id": ["The group id does not exist"]}})
        except TeamMemberDoesNotExistException:
            raise ValidationError(detail={"group": {"members": ["The member user id is not valid"]}})
        except TeamMemberEmailDoesNotExistException:
            raise ValidationError(detail={"group": {"members": ["The member emails are not valid"]}})
        except CipherBelongCollectionException:
            raise ValidationError(detail={"cipher": ["The cipher does not exist"]})
        except FolderDoesNotExistException:
            raise ValidationError(detail={"folder": ["The folder does not exist"]})
        except CipherBelongTeamException:
            raise ValidationError({"non_field_errors": [gen_error("5000")]})

        return Response(status=status.HTTP_200_OK, data=result)

    @action(methods=["post"], detail=False)
    def invitation_confirm(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request)
        personal_share = self.get_personal_share(kwargs.get("pk"))
        member_id = kwargs.get("member_id")
        key = request.data.get("key")
        if not key:
            raise ValidationError(detail={"key": ["This field is required"]})
        # Retrieve member that accepted
        try:
            member = self.sharing_service.get_shared_member(sharing_member_id=member_id)
            if member.status != PM_MEMBER_STATUS_ACCEPTED or member.team.team_id != personal_share.team_id:
                raise NotFound
        except TeamMemberDoesNotExistException:
            raise NotFound
        result = self.sharing_service.invitation_confirm(user=user, sharing_invitation=member, key=key)
        return Response(status=status.HTTP_200_OK, data=result)

    @action(methods=["put"], detail=False)
    def update_role(self, request, *args, **kwargs):
        self.check_pwd_session_auth(request)
        self.get_personal_share(sharing_id=kwargs.get("pk"))
        member_id = kwargs.get("member_id")
        # Retrieve member that accepted
        try:
            member = self.sharing_service.get_shared_member(sharing_member_id=member_id)
        except TeamMemberDoesNotExistException:
            raise NotFound

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        role = validated_data.get("role")
        hide_passwords = validated_data.get("hide_passwords", member.hide_passwords)

        try:
            self.sharing_service.update_role_invitation(
                member=member, role_id=role, hide_passwords=hide_passwords
            )
        except TeamMemberDoesNotExistException:
            raise NotFound
        return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(methods=["post"], detail=False)
    def invitation_group_confirm(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request)
        personal_share = self.get_personal_share(sharing_id=kwargs.get("pk"))
        group_id = kwargs.get("group_id")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        members_data = serializer.validated_data.get("members") or []
        try:
            self.sharing_service.invitation_group_confirm(
                user=user, sharing=personal_share, group_id=group_id, members=members_data
            )
        except TeamGroupDoesNotExistException:
            raise NotFound
        return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(methods=["put"], detail=False)
    def update_group_role(self, request, *args, **kwargs):
        self.check_pwd_session_auth(request)
        personal_share = self.get_personal_share(sharing_id=kwargs.get("pk"))
        group_id = kwargs.get("group_id")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        role = validated_data.get("role")
        try:
            self.sharing_service.update_group_role(
                sharing=personal_share, group_id=group_id, role_id=role
            )
        except TeamGroupDoesNotExistException:
            raise NotFound
        return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(methods=["get"], detail=False)
    def my_share(self, request, *args, **kwargs):
        self.check_pwd_session_auth(request=request)
        user = request.user
        my_shared_teams = self.sharing_service.list_my_share(
            user_id=user.user_id,
            type_param=self.request.query_params.get("type")
        )
        return Response(status=status.HTTP_200_OK, data=my_shared_teams)

    @action(methods=["post"], detail=False)
    def stop_share(self, request, *args, **kwargs):
        user = request.user
        self.check_pwd_session_auth(request)
        personal_share = self.get_personal_share(kwargs.get("pk"))
        member_id = kwargs.get("member_id")
        group_id = kwargs.get("group_id")

        # Check plan of the user
        self.allow_personal_sharing(user=user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()
        cipher = validated_data.get("cipher")
        personal_cipher_data = validated_data.get("personal_cipher_data")
        folder = validated_data.get("folder")

        try:
            self.sharing_service.stop_share(
                user=user, sharing=personal_share, member_id=member_id, group_id=group_id,
                cipher=cipher, personal_cipher_data=personal_cipher_data, folder=folder
            )
        except CipherDoesNotExistException:
            raise ValidationError(detail={"cipher": ["The cipher does not exist"]})
        except CollectionDoesNotExistException:
            raise ValidationError(detail={"folder": ["The folder does not exist"]})
        except StopCipherEmptyException:
            raise ValidationError(detail={"folder": ["The ciphers is not allow empty"]})
        except CipherBelongCollectionException:
            raise ValidationError(detail={"folder": ["The collection does not have the cipher"]})
        return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(methods=["post"], detail=False)
    def leave(self, request, *args, **kwargs):
        user = request.user
        self.check_pwd_session_auth(request)
        personal_share = self.get_personal_share(kwargs.get("pk"))
        # Retrieve member that accepted
        try:
            self.sharing_service.leave_sharing_team(user=user, sharing=personal_share)
        except TeamMemberDoesNotExistException:
            raise NotFound
        return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(methods=["post"], detail=False)
    def stop_share_cipher_folder(self, request, *args, **kwargs):
        user = request.user
        self.check_pwd_session_auth(request)
        personal_share = self.get_personal_share(sharing_id=kwargs.get("pk"))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()
        cipher = validated_data.get("cipher")
        personal_cipher_data = validated_data.get("personal_cipher_data")
        folder = validated_data.get("folder")

        try:
            personal_folder_id = self.sharing_service.stop_share_cipher_folder(
                user=user, sharing=personal_share,
                cipher=cipher, personal_cipher_data=personal_cipher_data, folder=folder
            )
        except CipherDoesNotExistException:
            raise ValidationError(detail={"cipher": ["The cipher does not exist"]})
        except CollectionDoesNotExistException:
            raise ValidationError(detail={"folder": ["The folder does not exist"]})
        except StopCipherEmptyException:
            raise ValidationError(detail={"folder": ["The ciphers is not allow empty"]})
        except CipherBelongCollectionException:
            raise ValidationError(detail={"folder": ["The collection does not have the cipher"]})
        return Response(status=status.HTTP_200_OK, data={"success": True, "personal_folder_id": personal_folder_id})

    @action(methods=["post"], detail=False)
    def add_member(self, request, *args, **kwargs):
        self.check_pwd_session_auth(request)
        personal_share = self.get_personal_share(kwargs.get("pk"))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        members = validated_data.get("members")
        groups = validated_data.get("groups")

        try:
            result = self.sharing_service.add_member(
                sharing=personal_share, members=members, groups=groups
            )
        except CollectionDoesNotExistException:
            raise NotFound
        except EnterpriseGroupDoesNotExistException:
            raise ValidationError(detail={"groups": {"id": ["The group id does not exist"]}})
        except TeamMemberDoesNotExistException:
            raise ValidationError(detail={"groups": {"members": ["The member user id is not valid"]}})
        except TeamMemberEmailDoesNotExistException:
            raise ValidationError(detail={"groups": {"members": ["The member emails are not valid"]}})
        return Response(status=status.HTTP_200_OK, data=result)

    @action(methods=["put"], detail=False)
    def update_share_folder(self, request, *args, **kwargs):
        user = request.user
        self.check_pwd_session_auth(request)
        personal_share = self.get_personal_share(kwargs.get("pk"))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        name = validated_data.get("name")

        try:
            collection = self.sharing_service.update_share_folder(
                user=user, sharing=personal_share, folder_id=kwargs.get("folder_id"), new_name=name
            )
        except CollectionDoesNotExistException:
            raise NotFound
        return Response(status=200, data={"id": collection.collection_id})

    @action(methods=["post"], detail=False)
    def delete_share_folder(self, request, *args, **kwargs):
        user = request.user
        self.check_pwd_session_auth(request)
        personal_share = self.get_personal_share(sharing_id=kwargs.get("pk"))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()
        folder = validated_data.get("folder")

        try:
            self.sharing_service.delete_share_folder(
                user=user, sharing=personal_share, folder=folder
            )
        except CollectionDoesNotExistException:
            raise ValidationError(detail={"folder": ["The folder does not exist"]})
        except StopCipherEmptyException:
            raise ValidationError(detail={"folder": ["The ciphers is not allow empty"]})
        except CipherBelongCollectionException:
            raise ValidationError(detail={"folder": ["The collection does not have the cipher"]})
        return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(methods=["post"], detail=False)
    def stop_share_folder(self, request, *args, **kwargs):
        user = request.user
        self.check_pwd_session_auth(request)
        personal_share = self.get_personal_share(sharing_id=kwargs.get("pk"))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()
        folder = validated_data.get("folder")

        try:
            personal_folder_id = self.sharing_service.stop_share_folder(
                user=user, sharing=personal_share, folder=folder
            )
        except CollectionDoesNotExistException:
            raise ValidationError(detail={"folder": ["The folder does not exist"]})
        except StopCipherEmptyException:
            raise ValidationError(detail={"folder": ["The ciphers is not allow empty"]})
        except CipherBelongCollectionException:
            raise ValidationError(detail={"folder": ["The collection does not have the cipher"]})
        return Response(status=200, data={"success": True, "personal_folder_id": personal_folder_id})

    @action(methods=["post"], detail=False)
    def add_item_share_folder(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request)
        personal_share = self.get_personal_share(sharing_id=kwargs.get("pk"))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()
        cipher_data = validated_data.get("cipher")

        try:
            self.sharing_service.add_item_share_folder(
                user=user, sharing=personal_share, folder_id=kwargs.get("folder_id"), cipher=cipher_data
            )
        except CollectionDoesNotExistException:
            raise ValidationError(detail={"folder": ["The folder does not exist"]})
        except CipherDoesNotExistException:
            raise ValidationError(detail={"cipher": {"id": ["The cipher id does not exist"]}})
        except CipherBelongTeamException:
            raise ValidationError({"non_field_errors": [gen_error("5000")]})
        return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(methods=["put"], detail=False)
    def remove_item_share_folder(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request)
        personal_share = self.get_personal_share(sharing_id=kwargs.get("pk"))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()
        cipher_data = validated_data.get("cipher")

        try:
            self.sharing_service.remove_item_share_folder(
                user=user, sharing=personal_share, folder_id=kwargs.get("folder_id"), cipher=cipher_data
            )
        except CollectionDoesNotExistException:
            raise ValidationError(detail={"folder": ["The folder does not exist"]})
        except CipherDoesNotExistException:
            raise ValidationError(detail={"cipher": {"id": ["The cipher id does not exist"]}})
        return Response(status=status.HTTP_200_OK, data={"success": True})
