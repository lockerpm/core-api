from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.enterprise_permissions.activity_log_pwd_permission import \
    ActivityLogPwdPermission
from locker_server.core.exceptions.enterprise_exception import EnterpriseDoesNotExistException
from locker_server.core.exceptions.enterprise_member_exception import EnterpriseMemberPrimaryDoesNotExistException
from locker_server.shared.constants.enterprise_members import *
from locker_server.shared.error_responses.error import gen_error
from locker_server.shared.utils.app import convert_readable_date, now
from .serializers import *


class ActivityLogPwdViewSet(APIBaseViewSet):
    permission_classes = (ActivityLogPwdPermission,)
    http_method_names = ["head", "options", "get", "post"]

    def get_serializer_class(self):
        if self.action == "list":
            self.serializer_class = ListActivityLogSerializer
        elif self.action == "retrieve":
            self.serializer_class = DetailActivityLogSerializer
        elif self.action == "export":
            self.serializer_class = ExportActivityLogSerializer
        elif self.action == "export_to_email":
            self.serializer_class = ExportEmailActivityLogSerializer
        return super().get_serializer_class()

    def get_enterprise(self):
        try:
            enterprise = self.enterprise_service.get_enterprise_by_id(
                enterprise_id=self.kwargs.get("pk")
            )
            self.check_object_permissions(request=self.request, obj=enterprise)
            # if enterprise.locked:
            #     raise ValidationError({"non_field_errors": [gen_error("3003")]})
            enterprise = self.check_allow_plan(enterprise=enterprise)
            return enterprise
        except EnterpriseDoesNotExistException:
            raise NotFound

    def check_allow_plan(self, enterprise):
        try:
            primary_member = self.enterprise_service.get_primary_member(
                enterprise_id=enterprise.enterprise_id
            )
        except EnterpriseMemberPrimaryDoesNotExistException:
            raise NotFound
        current_plan = self.user_service.get_current_plan(user=primary_member.user)
        plan = current_plan.pm_plan
        if plan.team_activity_log is False:
            raise ValidationError({"non_field_errors": [gen_error("7002")]})
        return enterprise

    def get_queryset(self):
        enterprise = self.get_enterprise()

        admin_only_param = self.request.query_params.get("admin_only", "0")
        member_only_param = self.request.query_params.get("member_only", "0")
        group_param = self.request.query_params.get("group")
        member_ids_param = self.request.query_params.get("member_ids")
        acting_member_ids_param = self.request.query_params.get("acting_member_ids")

        member_user_ids = []
        role_ids = []
        if admin_only_param == "1":
            role_ids += [E_MEMBER_ROLE_PRIMARY_ADMIN, E_MEMBER_ROLE_ADMIN]
        if member_only_param == "1":
            role_ids += [E_MEMBER_ROLE_MEMBER]
        if role_ids:
            member_user_ids += self.enterprise_member_service.list_enterprise_member_user_id_by_roles(
                enterprise_id=enterprise.enterprise_id,
                role_ids=role_ids
            )
        if member_ids_param:
            member_user_ids += self.enterprise_member_service.list_enterprise_member_user_id_by_members(
                enterprise_id=enterprise.enterprise_id,
                member_ids=member_ids_param.split(",")
            )
        if acting_member_ids_param:
            member_user_ids += self.enterprise_member_service.list_enterprise_member_user_id_by_members(
                enterprise_id=enterprise.enterprise_id,
                member_ids=acting_member_ids_param.split(",")
            )
        if group_param:
            member_user_ids += self.enterprise_member_service.list_enterprise_member_user_id_by_group_id(
                enterprise_id=enterprise.enterprise_id,
                group_id=group_param
            )
        filters = {
            "from": self.check_int_param(self.request.query_params.get("from")),
            "to": self.check_int_param(self.request.query_params.get("to")),
            "action": self.request.query_params.get("action"),
            "member_user_ids": member_user_ids,
            "enterprise_id": enterprise.enterprise_id
        }
        events = self.event_service.list_events(**filters)
        return events

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paging_param = self.request.query_params.get("paging", "1")
        page_size_param = self.check_int_param(self.request.query_params.get("size", 10))
        if paging_param == "0":
            self.pagination_class = None
        else:
            self.pagination_class.page_size = page_size_param if page_size_param else 10
        page = self.paginate_queryset(queryset)
        if page is not None:
            # TODO: check list logs
            normalize_page = self.event_service.normalize_enterprise_activity(activity_logs=page)
            serializer = self.get_serializer(normalize_page, many=True)
            return self.get_paginated_response(serializer.data)
        logs = self.event_service.normalize_enterprise_activity(activity_logs=queryset)
        serializer = self.get_serializer(logs, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(methods=["get"], detail=False)
    def export(self, request, *args, **kwargs):
        activity_logs_qs = self.get_queryset()
        enterprise = self.get_enterprise()
        enterprise_member = self.enterprise_member_service.get_member_by_user(
            user_id=request.user.user_id,
            enterprise_id=enterprise.enterprise_id
        )
        activity_logs = self.event_service.normalize_enterprise_activity(activity_logs=activity_logs_qs)
        context = self.get_serializer_context()
        context["use_html"] = False
        serializer = self.get_serializer(activity_logs, context=context, many=True)
        self.event_service.export_enterprise_activity(
            enterprise_member=enterprise_member, activity_logs=serializer.data
        )
        return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(methods=["post"], detail=False)
    def export_to_email(self, request, *args, **kwargs):
        to_param = self.check_int_param(self.request.query_params.get("to")) or now()
        from_param = self.check_int_param(self.request.query_params.get("from")) or now() - 30 * 86400
        to_param_str = convert_readable_date(to_param, "%m/%d/%Y %H:%M:%S") + " (UTC+00)"
        from_param_str = convert_readable_date(from_param, "%m/%d/%Y %H:%M:%S") + " (UTC+00)"

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        activity_logs_qs = self.get_queryset()
        enterprise = self.get_enterprise()
        enterprise_member = self.enterprise_member_service.get_member_by_user(
            user_id=request.user.user_id,
            enterprise_id=enterprise.enterprise_id
        )
        activity_logs = self.event_service.normalize_enterprise_activity(activity_logs=activity_logs_qs)
        serializer = ExportActivityLogSerializer(activity_logs, many=True)
        self.event_service.export_enterprise_activity(
            enterprise_member=enterprise_member,
            activity_logs=serializer.data,
            cc_emails=validated_data.get("cc", []),
            **{"to": to_param_str, "from": from_param_str}
        )
        return Response(status=status.HTTP_200_OK, data={"success": True})
