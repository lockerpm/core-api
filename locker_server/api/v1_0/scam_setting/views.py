from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status
from locker_server.api.api_base_view import APIBaseViewSet

from locker_server.core.exceptions.notification_setting_exception import NotificationSettingDoesNotExistException
from .serializers import *
from locker_server.api.permissions.locker_permissions.scam_setting_permission import ScamSettingPwdPermission


class ScamSettingPwdViewSet(APIBaseViewSet):
    permission_classes = (ScamSettingPwdPermission,)
    http_method_names = ["head", "options", "get", "put"]
    lookup_value_regex = r'[a-z_]+'

    def get_serializer_class(self):
        if self.action == "list":
            self.serializer_class = ScamSettingSerializer
        elif self.action == "update":
            self.serializer_class = UpdateScamSettingSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        query_params = self.request.query_params
        scam_settings = self.scam_setting_service.list_user_scam_settings(
            **{
                "user_id": user.user_id,
            }
        )
        return scam_settings

    def list(self, request, *args, **kwargs):
        paging_param = self.request.query_params.get("paging", "0")
        size_param = self.request.query_params.get("size", 10)
        page_size_param = self.check_int_param(size_param)
        if paging_param == "0":
            self.pagination_class = None
        else:
            self.pagination_class.page_size = page_size_param or 10
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        for data in validated_data:
            data.update({
                "user_id": user.user_id
            })
        scam_settings = self.scam_setting_service.create_multiple_scam_setting(
            list_create_data=validated_data,
            user_id=user.user_id
        )
        data = ScamSettingSerializer(scam_settings, many=True).data

        return Response(status=status.HTTP_200_OK, data=data)
