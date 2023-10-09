from datetime import timedelta, datetime
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.enterprise_permissions.enterprise_pwd_permission import \
    EnterprisePwdPermission
from locker_server.core.exceptions.country_exception import CountryDoesNotExistException
from locker_server.core.exceptions.enterprise_exception import EnterpriseDoesNotExistException
from locker_server.core.exceptions.enterprise_member_exception import EnterpriseMemberDoesNotExistException, \
    EnterpriseMemberPrimaryDoesNotExistException
from locker_server.shared.constants.enterprise_members import E_MEMBER_STATUS_CONFIRMED, E_MEMBER_STATUS_REQUESTED, \
    E_MEMBER_STATUS_INVITED
from locker_server.shared.constants.event import EVENT_ENTERPRISE_UPDATED
from locker_server.shared.constants.transactions import TRIAL_TEAM_PLAN
from locker_server.shared.error_responses.error import gen_error
from locker_server.shared.external_services.locker_background.constants import BG_EVENT
from locker_server.shared.utils.app import now
from .serializers import *


class EnterprisePwdViewSet(APIBaseViewSet):
    permission_classes = (EnterprisePwdPermission,)
    http_method_names = ["head", "options", "get", "post", "put", "delete"]
    lookup_value_regex = r'[0-9a-z]+'

    def get_serializer_class(self):
        if self.action == "list":
            self.serializer_class = ListEnterpriseSerializer
        elif self.action == "retrieve":
            self.serializer_class = DetailEnterpriseSerializer
        elif self.action in ["update"]:
            self.serializer_class = UpdateEnterpriseSerializer
        return super().get_serializer_class()

    def get_object(self):
        try:
            enterprise = self.enterprise_service.get_enterprise_by_id(
                enterprise_id=self.kwargs.get("pk")
            )
        except EnterpriseDoesNotExistException:
            raise NotFound
        self.check_object_permissions(request=self.request, obj=enterprise)
        if self.action in ["update"]:
            if enterprise.locked:
                raise ValidationError({"non_field_errors": [gen_error("3003")]})
        return enterprise

    def get_queryset(self):
        user = self.request.user
        enterprises = self.enterprise_service.list_user_enterprises(
            user_id=user.user_id,
            **{
                "status": E_MEMBER_STATUS_CONFIRMED
            }
        )
        return enterprises

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = self.filter_queryset(self.get_queryset())
        paging_param = self.request.query_params.get("paging", "1")
        page_size_param = self.check_int_param(self.request.query_params.get("size", 10))
        if paging_param == "0":
            self.pagination_class = None
        else:
            self.pagination_class.page_size = page_size_param if page_size_param else 10
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            normalize_data = self.normalize_enterprise(serializer.data, user=user)
            return self.get_paginated_response(normalize_data)

        serializer = self.get_serializer(queryset, many=True)
        normalize_data = self.normalize_enterprise(serializer.data, user=user)
        return Response(status=status.HTTP_200_OK, data=normalize_data)

    def retrieve(self, request, *args, **kwargs):
        enterprise = self.get_object()

        serializer = self.get_serializer(enterprise, many=False)
        normalize_data = self.normalize_enterprise(
            enterprises_data=[serializer.data],
            user=request.user
        )[0]
        return Response(status=status.HTTP_200_OK, data=normalize_data)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        ip = request.data.get("ip")
        enterprise = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        try:
            updated_enterprise = self.enterprise_service.update_enterprise(
                enterprise_id=enterprise.enterprise_id,
                enterprise_update_data=validated_data
            )
        except CountryDoesNotExistException:
            raise ValidationError(detail={"enterprise_country": ["The country does not exist"]})
        except EnterpriseDoesNotExistException:
            raise NotFound
        # Log update activity here
        # TODO: import LockerBackgroundFactory
        LockerBackgroundFactory.get_background(bg_name=BG_EVENT).run(func_name="create_by_enterprise_ids", **{
            "enterprise_ids": [enterprise.id], "acting_user_id": user.user_id, "user_id": user.user_id,
            "type": EVENT_ENTERPRISE_UPDATED, "ip_address": ip
        })
        updated_enterprise = self.normalize_enterprise([updated_enterprise])[0]
        serializer = DetailEnterpriseSerializer(updated_enterprise, many=False)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        enterprise = self.get_object()
        # Cancel the plan of the owner
        primary_admin = self.enterprise_service.get_primary_member(
            enterprise_id=enterprise.enterprise_id
        )
        self.user_service.cancel_plan(user=primary_admin, immediately=True)

        self.enterprise_service.delete_enterprise_complete(
            enterprise=enterprise
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["get"], detail=True)
    def dashboard(self, request, *args, **kwargs):
        enterprise = self.get_object()
        from_param = self.check_int_param(self.request.query_params.get("from", now() - 7 * 86400))
        to_param = self.check_int_param(self.request.query_params.get("to", now()))

        # Member statistic
        members = self.enterprise_member_service.list_enterprise_members(**{
            "enterprise_id": enterprise.enterprise_id

        })
        e_members_status_confirmed_count = 0
        e_member_status_requested_count = 0
        e_member_status_invited_count = 0
        members_activated_count = 0
        weak_master_password_count = 0
        confirmed_user_ids = []
        leaked_account_count = 0
        being_blocked_login = []
        for member in members:
            status = member.status
            is_activated = member.is_activated
            master_password_score = member.user.master_password_score
            if status == E_MEMBER_STATUS_CONFIRMED:
                e_members_status_confirmed_count += 1
                confirmed_user_ids.append(member.user.user_id)
            elif status == E_MEMBER_STATUS_REQUESTED:
                e_member_status_requested_count += 1
            elif status == E_MEMBER_STATUS_INVITED:
                e_member_status_invited_count += 1
            # Count activated member
            if status == E_MEMBER_STATUS_CONFIRMED and is_activated:
                members_activated_count += 1
            # Master Password statistic
            if status == E_MEMBER_STATUS_CONFIRMED and master_password_score <= 1:
                weak_master_password_count += 1
            # Leak statistic
            if status == E_MEMBER_STATUS_CONFIRMED and member.user.is_leaked == True:
                leaked_account_count += 1

            # Failed login
            if status == E_MEMBER_STATUS_CONFIRMED and member.user.login_block_until and member.user.login_block_until >= now():
                being_blocked_login.append({
                    "id": member.enterprise_member_id,
                    "user_id": member.user.user_id,
                    "blocked_time": member.user.last_request_login
                })

        members_status_statistic = {
            E_MEMBER_STATUS_CONFIRMED: e_members_status_confirmed_count,
            E_MEMBER_STATUS_REQUESTED: e_member_status_requested_count,
            E_MEMBER_STATUS_INVITED: e_member_status_invited_count,
        }

        # Cipher Password statistic
        weak_cipher_password_count = self.user_service.count_weak_cipher_password(user_ids=confirmed_user_ids)
        # Un-verified domain
        unverified_domain_count = self.enterprise_service.count_unverified_domain(
            enterprise_id=enterprise.enterprise_id
        )

        return Response(status=200, data={
            "members": {
                "total": len(members),
                "status": members_status_statistic,
                "billing_members": members_activated_count,
            },
            "login_statistic": self._statistic_login_by_time(
                enterprise_id=enterprise.enterprise_id, user_ids=confirmed_user_ids, from_param=from_param,
                to_param=to_param
            ),
            "password_security": {
                "weak_master_password": weak_master_password_count,
                "weak_password": weak_cipher_password_count,
                "leaked_account": leaked_account_count
            },
            "block_failed_login": being_blocked_login,
            # "blocking_login": blocking_login,
            "unverified_domain": unverified_domain_count
        })

    def _statistic_login_by_time(self, enterprise_id, user_ids, from_param, to_param):
        start_date = datetime.fromtimestamp(from_param)
        end_date = datetime.fromtimestamp(to_param)
        durations_list = []
        for i in range((end_date - start_date).days + 1):
            date = start_date + timedelta(days=i)
            d = "{}-{:02}-{:02}".format(date.year, date.month, date.day)
            durations_list.append(d)

        data = dict()
        for d in sorted(set(durations_list), reverse=True):
            data[d] = 0
        login_events = self.event_service.statistic_login_by_time(
            enterprise_id=enterprise_id,
            user_ids=user_ids,
            from_param=from_param,
            to_param=to_param
        )

        data.update(login_events)
        return data

    def normalize_enterprise(self, enterprises_data, user=None):
        for enterprise_data in enterprises_data:
            enterprise_id = enterprise_data.get("id")
            try:
                if user:
                    member = self.enterprise_member_service.get_member_by_user(
                        user_id=user.user_id,
                        enterprise_id=enterprise_id
                    )
                    enterprise_data.update({
                        "role": member.role.name,
                        "is_default": member.is_default
                    })
                else:
                    enterprise_data.update({
                        "role": None,
                        "is_default": None
                    })
                primary_admin = self.enterprise_service.get_primary_member(
                    enterprise_id=enterprise_id
                )
                if primary_admin:
                    enterprise_data.update({
                        "primary_admin": primary_admin.user.user_id
                    })
                    current_admin_plan = self.user_service.get_current_plan(user=primary_admin.user)
                    if current_admin_plan:
                        is_trialing = current_admin_plan.end_period and current_admin_plan.end_period - current_admin_plan.start_period < TRIAL_TEAM_PLAN
                        enterprise_data.update({
                            "is_trialing": is_trialing,
                            "end_period": current_admin_plan.end_period,
                        })
                    else:
                        enterprise_data.update({
                            "is_trialing": None,
                            "end_period": None,
                        })
                else:
                    enterprise_data.update({
                        "primary_admin": None
                    })
            except EnterpriseMemberDoesNotExistException:
                pass
            except EnterpriseMemberPrimaryDoesNotExistException:
                pass

        return enterprises_data
