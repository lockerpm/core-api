from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.core.exceptions.whitelist_scam_url_exception import WhitelistScamUrlDoesNotExistException, \
    WhitelistScamUrlExistedException
from locker_server.shared.external_services.pm_sync import PwdSync, SYNC_EVENT_SCAM_SETTING_UPDATE, \
    SYNC_EVENT_WHITELIST_URL_CREATE, SYNC_EVENT_WHITELIST_URL_UPDATE, SYNC_EVENT_WHITELIST_URL_DELETE

from .serializers import *
from locker_server.api.permissions.locker_permissions.scam_setting_permission import ScamSettingPwdPermission


class ScamSettingPwdViewSet(APIBaseViewSet):
    permission_classes = (ScamSettingPwdPermission,)
    http_method_names = ["head", "options", "get", "put", "post", "delete"]
    lookup_value_regex = r'[a-z_]+'

    def get_serializer_class(self):
        if self.action == "list":
            self.serializer_class = ScamSettingSerializer
        elif self.action == "update":
            self.serializer_class = UpdateScamSettingSerializer
        elif self.action == "list_wl_urls":
            self.serializer_class = ListWlScamUrlSerializer
        elif self.action == 'retrieve_wl_url':
            self.serializer_class = DetailWlScamUrlSerializer
        elif self.action == "update_wl_url":
            self.serializer_class = UpdateWlScamUrlSerializer
        elif self.action == "create_wl_url":
            self.serializer_class = CreateWlScamUrlSerializer

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

    def get_wl_url_queryset(self):
        user = self.request.user
        query_params = self.request.query_params
        wl_urls = self.scam_setting_service.list_wl_scam_urls(**{
            "user_id": user.user_id,
            "q": query_params.get("q"),
        })
        return wl_urls

    def get_wl_url_object(self):
        try:
            wl_url = self.scam_setting_service.get_wl_scam_url(
                wl_url_id=self.kwargs.get("wl_url_id")
            )
            self.check_object_permissions(request=self.request, obj=wl_url)
            return wl_url
        except WhitelistScamUrlDoesNotExistException:
            raise NotFound

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
        PwdSync(event=SYNC_EVENT_SCAM_SETTING_UPDATE, user_ids=[user.user_id], team=None, add_all=False).send(
            data={"data": data}
        )
        return Response(status=status.HTTP_200_OK, data=data)

    def list_wl_urls(self, request, *args, **kwargs):
        paging_param = self.request.query_params.get("paging", "1")
        size_param = self.request.query_params.get("size", 10)
        page_size_param = self.check_int_param(size_param)
        if paging_param == "0":
            self.pagination_class = None
        else:
            self.pagination_class.page_size = page_size_param or 10
        queryset = self.get_wl_url_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update_wl_url(self, request, *args, **kwargs):
        wl_scam_url = self.get_wl_url_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            updated_wl_url = self.scam_setting_service.update_wl_scam_url(
                user_id=self.request.user.user_id,
                wl_url_id=wl_scam_url.whitelist_scam_url_id,
                **validated_data,
            )
        except WhitelistScamUrlDoesNotExistException:
            raise NotFound
        except WhitelistScamUrlExistedException:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"details": ["Whitelist scam url already exists"]})
        PwdSync(event=SYNC_EVENT_WHITELIST_URL_UPDATE, user_ids=[request.user.user_id]).send(
            data={"id": str(updated_wl_url.wl_url_id)}
        )
        return Response(status=status.HTTP_200_OK, data=DetailWlScamUrlSerializer(updated_wl_url, many=False).data)

    def create_wl_url(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data.update({
            "user_id": user.user_id
        })
        new_wl_url = self.scam_setting_service.create_wl_scam_url(**validated_data)
        PwdSync(event=SYNC_EVENT_WHITELIST_URL_CREATE, user_ids=[request.user.user_id]).send(
            data={"id": str(new_wl_url.wl_url_id)}
        )
        return Response(status=status.HTTP_200_OK, data=DetailWlScamUrlSerializer(new_wl_url).data)

    def retrieve_wl_url(self, request, *args, **kwargs):
        instance = self.get_wl_url_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy_wl_url(self, request, *args, **kwargs):
        instance = self.get_wl_url_object()
        self.scam_setting_service.delete_wl_scam_url(instance.whitelist_scam_url_id)
        PwdSync(event=SYNC_EVENT_WHITELIST_URL_DELETE, user_ids=[request.user.user_id]).send(
            data={"id": str(instance.wl_url_id)}
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
