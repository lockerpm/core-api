from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied

from locker_server.core.entities.enterprise.enterprise import Enterprise
from locker_server.core.exceptions.enterprise_exception import EnterpriseDoesNotExistException
from locker_server.core.exceptions.enterprise_member_exception import EnterpriseMemberDoesNotExistException, \
    EnterpriseMemberUpdatedFailedException, EnterpriseMemberInvitationUpdatedFailedException
from locker_server.core.exceptions.payment_exception import PaymentMethodNotSupportException
from locker_server.shared.constants.enterprise_members import E_MEMBER_ROLE_PRIMARY_ADMIN, E_MEMBER_ROLE_ADMIN, \
    E_MEMBER_STATUS_REQUESTED
from locker_server.shared.constants.event import EVENT_E_MEMBER_UPDATED_ROLE, EVENT_E_MEMBER_CONFIRMED, \
    EVENT_E_MEMBER_ENABLED, EVENT_E_MEMBER_REMOVED, EVENT_E_MEMBER_DISABLED
from locker_server.shared.constants.transactions import PAYMENT_METHOD_CARD
from locker_server.shared.error_responses.error import gen_error
from locker_server.shared.external_services.locker_background.constants import BG_EVENT
from locker_server.shared.external_services.payment_method.payment_method_factory import PaymentMethodFactory
from locker_server.shared.utils.app import now
from .serializers import *
from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.enterprise_permissions.member_pwd_permission import \
    MemberPwdPermission


class MemberPwdViewSet(APIBaseViewSet):
    permission_classes = (MemberPwdPermission,)
    lookup_value_regex = r'[0-9a-z\-]+'
    http_method_names = ["head", "options", "get", "post", "put", "delete"]

    def get_serializer_class(self):
        if self.action == "list":
            shortly_param = self.request.query_params.get("shortly", "0")
            if shortly_param == "1":
                self.serializer_class = ShortDetailMemberSerializer
            else:
                self.serializer_class = DetailMemberSerializer
        elif self.action == "retrieve":
            self.serializer_class = DetailActiveMemberSerializer
        elif self.action == "update":
            self.serializer_class = UpdateMemberSerializer
        elif self.action == "user_invitations":
            self.serializer_class = UserInvitationSerializer
        elif self.action == "user_invitation_update":
            self.serializer_class = UpdateUserInvitationSerializer
        elif self.action == "activated":
            self.serializer_class = EnabledMemberSerializer
        elif self.action == "search_members_groups":
            self.serializer_class = SearchMemberGroupSerializer
        return super().get_serializer_class()

    def get_object(self):
        try:
            enterprise = self.enterprise_service.get_enterprise_by_id(
                enterprise_id=self.kwargs.get("pk")
            )
            self.check_object_permissions(request=self.request, obj=enterprise)
            # if self.action in ["create", "update", "create_multiple", "activated", ]:
            if self.request.method in ["POST", "PUT", "DELETE"] and enterprise.locked and \
                    self.action not in ["activated", "destroy"]:
                raise ValidationError({"non_field_errors": [gen_error("3003")]})
            return enterprise
        except EnterpriseDoesNotExistException:
            raise NotFound

    def get_enterprise_member(self, enterprise: Enterprise, member_id):
        try:
            member = self.enterprise_member_service.get_member_by_id(
                member_id=member_id
            )
            if member.enterprise.enterprise_id != enterprise.enterprise_id:
                raise NotFound
            return member
        except EnterpriseMemberDoesNotExistException:
            raise NotFound

    def get_queryset(self):
        enterprise = self.get_object()
        query_params = self.request.query_params

        # Get list role to filter
        filter_primary_admin_param = query_params.get("primary_admin", "0")
        filter_admin_param = query_params.get("admin", "0")
        filter_member_param = query_params.get("member", "0")
        list_filter_roles = []
        if filter_primary_admin_param == "1":
            list_filter_roles.append(E_MEMBER_ROLE_PRIMARY_ADMIN)
        if filter_admin_param == "1":
            list_filter_roles.append(E_MEMBER_ROLE_ADMIN)
        if filter_member_param == "1":
            list_filter_roles.append(E_MEMBER_ROLE_MEMBER)

        members = self.enterprise_member_service.list_enterprise_members(**{
            "enterprise_id": enterprise.enterprise_id,
            "user_ids": query_params.get("user_ids", "").split(","),
            "email": query_params.get("email", None),
            "roles": list_filter_roles,
            "status": query_params.get("status"),
            "statuses": query_params.get("statuses", "").split(","),
            "is_activated": query_params.get("is_activated"),
            "block_login": query_params.get("block_login"),
            "sort": query_params.get("sort"),

        })
        shortly_param = query_params.get("shortly", "0")
        if shortly_param == "1":
            for member in members:
                group_members = self.enterprise_member_service.list_group_member_by_enterprise_member_id(
                    enterprise_member_id=member.enterprise_member_id
                )
                member.group_members = group_members
        return members

    def list(self, request, *args, **kwargs):
        paging_param = self.request.query_params.get("paging", "1")
        page_size_param = self.check_int_param(self.request.query_params.get("size", 10))
        if paging_param == "0":
            self.pagination_class = None
        else:
            self.pagination_class.page_size = page_size_param if page_size_param else 10

        return super().list(request, *args, **kwargs)

    @action(methods=["post"], detail=False)
    def create_multiple(self, request, *args, **kwargs):
        ip = request.data.get("ip")
        members = request.data.get("members")
        if not isinstance(members, list):
            raise ValidationError(detail={"members": ["Members are not valid. This field must be an array"]})

        enterprise = self.get_object()
        added_members, non_added_members = self.enterprise_member_service.create_multiple_member(
            current_enterprise=enterprise,
            members_data=members
        )
        return Response(
            status=status.HTTP_200_OK,
            data={
                "enterprise_id": enterprise.id,
                "enterprise_name": enterprise.name,
                "members": added_members,
                "non_added_members": non_added_members
            }
        )

    @action(methods=["post"], detail=False)
    def invitation_multiple(self, request, *args, **kwargs):
        """
        Create members obj for non-exist users
        """
        ip = request.data.get("ip")
        user = self.request.user
        members_data = request.data.get("members", [])
        if not isinstance(members_data, list):
            raise ValidationError(detail={"members": ["Members are not valid. This field must be an array"]})
        enterprise = self.get_object()
        added_members, non_added_members = self.enterprise_member_service.invite_multiple_member(
            secret=settings.SECRET_KEY,
            current_enterprise=enterprise.enterprise_id,
            members_data=members_data,
            scope=settings.SCOPE_PWD_MANAGER
        )

        return Response(
            status=status.HTTP_200_OK,
            data={
                "members": added_members,
                "non_added_members": non_added_members
            }
        )

    def retrieve(self, request, *args, **kwargs):
        enterprise = self.get_object()
        member_id = kwargs.get("member_id")
        enterprise_member = self.get_enterprise_member(enterprise=enterprise, member_id=member_id)
        # TODO: get cipher_overview of member
        cipher_overview = {}
        if enterprise_member.user and enterprise_member.status != E_MEMBER_STATUS_INVITED:
            cipher_overview = self.user_service.get_user_cipher_overview(
                user_id=enterprise_member.user.user_id
            )
        enterprise_member.cipher_overview = cipher_overview
        serializer = self.get_serializer(enterprise_member)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, *args, **kwargs):
        ip = request.data.get("ip")
        user = self.request.user
        enterprise = self.get_object()
        member_id = kwargs.get("member_id")
        enterprise_member = self.get_enterprise_member(enterprise=enterprise, member_id=member_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        role = validated_data.get("role")
        status = validated_data.get("status")
        try:
            change_status, change_role, updated_member = self.enterprise_member_service.update_enterprise_member(
                current_user=user,
                enterprise_member=enterprise_member,
                role=role,
                status=status
            )
        except EnterpriseMemberUpdatedFailedException:
            raise PermissionDenied
        except EnterpriseMemberDoesNotExistException:
            raise NotFound
        if change_role:
            # TODO: import LockerBackgroundFactory
            LockerBackgroundFactory.get_background(bg_name=BG_EVENT).run(
                func_name="create_by_enterprise_ids",
                **{
                    "enterprise_ids": [updated_member.enterprise.enterprise_id],
                    "acting_user_id": user.user_id,
                    "user_id": updated_member.user.user_id,
                    "team_member_id": updated_member.enterprise_member_id,
                    "type": EVENT_E_MEMBER_UPDATED_ROLE, "ip_address": ip,
                    "metadata": {"old_role": enterprise_member.role.name, "new_role": role}
                }
            )
        if change_status:
            # TODO: import LockerBackgroundFactory
            LockerBackgroundFactory.get_background(bg_name=BG_EVENT).run(
                func_name="create_by_enterprise_ids",
                **{
                    "enterprise_ids": [updated_member.enterprise.enterprise_id],
                    "acting_user_id": user.user_id,
                    "user_id": updated_member.user.user_id,
                    "team_member_id": updated_member.enterprise_member_id,
                    "type": EVENT_E_MEMBER_CONFIRMED, "ip_address": ip
                }
            )
            is_billing_added = self.is_billing_members_added(
                enterprise_member=updated_member
            )
            if is_billing_added:
                try:
                    primary_user = self.enterprise_service.get_primary_member(enterprise_id=enterprise.enterprise_id)
                    user_plan = self.user_service.get_current_plan(user=primary_user)
                    PaymentMethodFactory.get_method(
                        user_plan=user_plan,
                        scope=settings.SCOPE_PWD_MANAGER,
                        payment_method=PAYMENT_METHOD_CARD
                    ).update_quantity_subscription(amount=1)
                except (PaymentMethodNotSupportException, ObjectDoesNotExist):
                    pass
        return Response(
            status=status.HTTP_200_OK,
            data={
                "success": True,
                "change_status": change_status,
                "change_role": change_role,
                "member_id": updated_member.enterprise_member_id,
                "member_user_id": updated_member.user.user_id,
                "enterprise_name": updated_member.enterprise.name,
                "status": updated_member.status,
                "role": updated_member.role.name
            }
        )

    def destroy(self, request, *args, **kwargs):
        ip = request.data.get("ip")
        user = self.request.user
        enterprise = self.get_object()
        enterprise_member = self.get_enterprise_member(enterprise=enterprise, member_id=kwargs.get("member_id"))
        deleted_member_user_id = enterprise_member.user.user_id
        deleted_member_status = enterprise_member.status
        # Not allow delete themselves
        if enterprise_member.user.user_id == user.user_id or enterprise_member.role.name == E_MEMBER_ROLE_PRIMARY_ADMIN:
            raise PermissionDenied
        try:
            self.enterprise_member_service.delete_enterprise_member(
                enterprise_member_id=enterprise_member.enterprise_member_id)
        except EnterpriseMemberDoesNotExistException:
            raise NotFound
        try:
            primary_user = self.enterprise_service.get_primary_member(enterprise_id=enterprise.enterprise_id)
            current_plan = self.user_service.get_current_plan(user=primary_user)
            PaymentMethodFactory.get_method(
                user_plan=current_plan, scope=settings.SCOPE_PWD_MANAGER,
                payment_method=PAYMENT_METHOD_CARD
            ).update_quantity_subscription(amount=-1)
        except (PaymentMethodNotSupportException, ObjectDoesNotExist):
            pass

        # Log activity delete member here
        # TODO: import LockerBackgroundFactory
        LockerBackgroundFactory.get_background(bg_name=BG_EVENT).run(func_name="create_by_enterprise_ids", **{
            "enterprise_ids": [enterprise.enterprise_id], "acting_user_id": user.user_id,
            "user_id": enterprise_member.user.user_id, "team_member_id": enterprise_member.enterprise_member_id,
            "type": EVENT_E_MEMBER_REMOVED, "ip_address": ip,
        })

        return Response(
            status=status.HTTP_200_OK,
            data={
                "enterprise_id": enterprise.enterprise_id,
                "enterprise_name": enterprise.name,
                "member_user_id": deleted_member_user_id,
                "member_status": deleted_member_status,
            }
        )

    @action(methods=["post"], detail=False)
    def reinvite(self, request, *args, **kwargs):
        enterprise = self.get_object()
        enterprise_member = self.get_enterprise_member(enterprise=enterprise, member_id=kwargs.get("member_id"))
        if enterprise_member.status != E_MEMBER_STATUS_INVITED or enterprise_member.domain:
            raise NotFound
        return Response(
            status=status.HTTP_200_OK,
            data={
                "user_id": enterprise_member.user.user_id,
                "email": enterprise_member.email,
                "token_invitation": enterprise_member.token_invitation,
                "enterprise_id": enterprise.enterprise_id,
                "enterprise_name": enterprise.name
            }
        )

    @action(methods=["put"], detail=False)
    def activated(self, request, *args, **kwargs):
        user = self.request.user
        ip = request.data.get("ip")
        enterprise = self.get_object()
        enterprise_member = self.get_enterprise_member(enterprise=enterprise, member_id=kwargs.get("member_id"))

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        activated = validated_data.get("activated")
        if enterprise_member.is_activated != activated:
            try:
                updated_enterprise_member = self.enterprise_member_service.activated_member(
                    activated=activated,
                    enterprise_member=enterprise_member,
                    current_user=user
                )
            except EnterpriseMemberDoesNotExistException:
                raise NotFound
            except EnterpriseMemberUpdatedFailedException:
                raise PermissionDenied
            primary_user = self.enterprise_service.get_primary_member(enterprise_id=enterprise.enterprise_id)
            current_plan = self.user_service.get_current_plan(user=primary_user)
            # Remove this member from all groups
            if activated is False:
                self.enterprise_member_service.delete_group_members_by_member_id(
                    enterprise_member_id=enterprise_member.enterprise_member_id
                )
            #  Update billing here - Check the user is a new activated user in billing period
            if activated is True and self.is_billing_members_added(enterprise_member=updated_enterprise_member):
                try:
                    PaymentMethodFactory.get_method(
                        user_plan=current_plan, scope=settings.SCOPE_PWD_MANAGER,
                        payment_method=PAYMENT_METHOD_CARD
                    ).update_quantity_subscription(amount=1)
                except (PaymentMethodNotSupportException, ObjectDoesNotExist):
                    pass
            if activated is False and self.is_billing_members_removed(enterprise_member=enterprise_member):
                try:
                    PaymentMethodFactory.get_method(
                        user_plan=current_plan, scope=settings.SCOPE_PWD_MANAGER,
                        payment_method=PAYMENT_METHOD_CARD
                    ).update_quantity_subscription(amount=-1)
                except (PaymentMethodNotSupportException, ObjectDoesNotExist):
                    pass
            # TODO: import LockerBackgroundFactory
            LockerBackgroundFactory.get_background(bg_name=BG_EVENT).run(func_name="create_by_enterprise_ids", **{
                "enterprise_ids": [enterprise.enterprise_id], "acting_user_id": user.user_id,
                "user_id": enterprise_member.user.user_id, "team_member_id": enterprise_member.enterprise_member_id,
                "type": EVENT_E_MEMBER_ENABLED if activated is True else EVENT_E_MEMBER_DISABLED, "ip_address": ip
            })
            return Response(
                status=status.HTTP_200_OK,
                data={
                    "success": True, "notification": True,
                    "member_user_id": enterprise_member.user.user_id,
                    "enterprise_name": enterprise_member.enterprise.name,
                    "activated": activated
                }
            )

        return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(methods=["put"], detail=False)
    def unblock(self, request, *args, **kwargs):
        user = self.request.user
        enterprise = self.get_object()
        enterprise_member = self.get_enterprise_member(enterprise=enterprise, member_id=kwargs.get("member_id"))
        try:
            self.enterprise_member_service.unblock_enterprise_member(
                current_user=user,
                enterprise_member=enterprise_member
            )
        except EnterpriseMemberDoesNotExistException:
            raise NotFound
        except EnterpriseMemberUpdatedFailedException:
            raise PermissionDenied

        return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(methods=["get"], detail=False)
    def user_invitations(self, request, *args, **kwargs):
        user = self.request.user
        member_invitations = self.enterprise_member_service.list_enterprise_members(**{
            "user_id": user.user_id,
            "statuses": [E_MEMBER_STATUS_INVITED, E_MEMBER_STATUS_REQUESTED]
        })
        for member_invitation in member_invitations:
            primary_user = self.enterprise_service.get_primary_member(
                enterprise_id=member_invitation.enterprise.enterprise_id
            )
            member_invitation.owner = primary_user.user.user_id
        serializer = self.get_serializer(member_invitations, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(methods=["put"], detail=False)
    def user_invitation_update(self, request, *args, **kwargs):
        user = self.request.user
        ip = request.data.get("ip")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        status = validated_data.get("status")
        if status not in ["confirmed", "reject"]:
            raise ValidationError(detail={"status": ["This status is not valid"]})
        try:
            updated_member_invitation = self.enterprise_member_service.update_user_invitations(
                current_user=user,
                enterprise_member_id=kwargs.get("pk"),
                status=status
            )
        except EnterpriseMemberDoesNotExistException:
            raise NotFound
        except EnterpriseMemberInvitationUpdatedFailedException:
            raise ValidationError(detail={"status": ["You cannot reject this enterprise"]})
        enterprise = updated_member_invitation.enterprise

        primary_admin_user = self.enterprise_service.get_primary_member(enterprise_id=enterprise.enterprise_id)
        admin_plan = self.user_service.get_current_plan(primary_admin_user)
        if not primary_admin_user:
            primary_admin_user_id = None
        else:
            primary_admin_user_id = primary_admin_user.user.user_id
        admin_members = self.enterprise_member_service.list_enterprise_members(**{
            "enterprise_id": enterprise.enterprise_id,
            "roles": [E_MEMBER_ROLE_ADMIN],
            "status": E_MEMBER_STATUS_CONFIRMED
        })
        admin_user_ids = [admin_member.user.user_id for admin_member in admin_members]

        member_status = updated_member_invitation.status if status != "reject" else None
        if member_status == E_MEMBER_STATUS_CONFIRMED:
            # Log event
            LockerBackgroundFactory.get_background(bg_name=BG_EVENT).run(func_name="create_by_enterprise_ids", **{
                "enterprise_ids": [enterprise.enterprise_id], "acting_user_id": user.user_id,
                "user_id": user.user_id, "team_member_id": updated_member_invitation.enterprise_member_id,
                "type": EVENT_E_MEMBER_CONFIRMED, "ip_address": ip
            })
            # Update subscription quantity here
            if self.is_billing_members_added(
                    enterprise_member=updated_member_invitation) is True and primary_admin_user:
                try:
                    PaymentMethodFactory.get_method(
                        user_plan=admin_plan, scope=settings.SCOPE_PWD_MANAGER, payment_method=PAYMENT_METHOD_CARD
                    ).update_quantity_subscription(amount=1)
                except PaymentMethodNotSupportException:
                    pass

        return Response(
            status=status.HTTP_200_OK,
            data={
                "success": True,
                "member_status": member_status,
                "primary_owner": primary_admin_user_id,
                "admin": admin_user_ids,
                "enterprise_name": enterprise.name,
            }
        )

    @action(methods=["get"], detail=False)
    def invitation_confirmation(self, request, *args, **kwargs):
        email = self.request.query_params.get("email")
        user_id = self.request.query_params.get("user_id")
        if not email or not user_id:
            raise NotFound
        enterprise_ids = self.enterprise_member_service.confirm_invitation(user_id=user_id, email=email)
        return Response(status=status.HTTP_200_OK, data={"enterprise_ids": enterprise_ids})

    @action(methods=["post"], detail=False)
    def search_members_groups(self, request, *args, **kwargs):
        user = self.request.user
        enterprise = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        query = validated_data.get("query")
        user_ids = validated_data.get("user_ids") or []
        status = validated_data.get("status", E_MEMBER_STATUS_CONFIRMED)
        members = self.enterprise_member_service.list_enterprise_members(**{
            "enterprise_id": enterprise.enterprise_id,
            "user_ids": user_ids,
            "status": status
        })[:5]
        groups = self.enterprise_group_service.list_enterprise_groups(
            enterprise_id=enterprise.enterprise_id,
            **{
                "name": query.lower()
            }
        )[:5]

        members_serializer = ShortDetailMemberSerializer(members, many=True)
        groups_serializer = EnterpriseGroupSerializer(groups, many=True)
        return Response(
            status=status.HTTP_200_OK,
            data={
                "members": members_serializer.data,
                "groups": groups_serializer.data
            }
        )

    def is_billing_members_added(self, enterprise_member: EnterpriseMember) -> bool:
        enterprise = enterprise_member.enterprise
        primary_user = self.enterprise_service.get_primary_member(enterprise_id=enterprise.enterprise_id)
        current_plan = self.user_service.get_current_plan(user=primary_user)
        from_param = current_plan.start_period if current_plan.start_period else current_plan.creation_date
        to_param = current_plan.end_period if current_plan.end_period else now()
        events = self.event_service.list_events(**{
            "team_id": enterprise.enterprise_id,
            "types": [EVENT_E_MEMBER_ENABLED, EVENT_E_MEMBER_CONFIRMED],
            "user_id": enterprise_member.user.user_id,
            "creation_date_range": (from_param, to_param)

        })
        if not events:
            return True
        return False

    def is_billing_members_removed(self, enterprise_member: EnterpriseMember) -> bool:
        enterprise = enterprise_member.enterprise
        primary_user = self.enterprise_service.get_primary_member(enterprise_id=enterprise.enterprise_id)
        current_plan = self.user_service.get_current_plan(user=primary_user)
        from_param = current_plan.start_period if current_plan.start_period else current_plan.creation_date
        to_param = current_plan.end_period if current_plan.end_period else now()
        events = self.event_service.list_events(**{
            "team_id": enterprise.enterprise_id,
            "types": [EVENT_E_MEMBER_DISABLED, EVENT_E_MEMBER_REMOVED],
            "user_id": enterprise_member.user.user_id,
            "creation_date_range": (from_param, to_param)

        })
        if not events:
            return True
        return False
