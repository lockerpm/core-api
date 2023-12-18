import json

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet

from .serializers import *
from locker_server.api.permissions.admin_permissions.admin_app_info_permission import AdminAppInfoPermission


class AdminAppInfoViewSet(APIBaseViewSet):
    permission_classes = (AdminAppInfoPermission,)
    http_method_names = ["options", "head", "get", "post", "put", "delete"]
    lookup_value_regex = r'[0-9a-z]+'

    def get_throttles(self):
        return super().get_throttles()

    def get_serializer_class(self):
        if self.action == "update_app_info":
            self.serializer_class = UpdateAppInfoSerializer
        elif self.action == "app_info_logo":
            if self.request.method == "PUT":
                self.serializer_class = UpdateAppLogoSerializer
        return super().get_serializer_class()

    def get_object(self):
        app_info = self.app_info_service.get_app_info()
        self.check_object_permissions(request=self.request, obj=app_info)
        return app_info

    @action(methods=["get"], detail=False)
    def app_info(self, request, *args, **kwargs):
        app_info = self.get_object()
        if not app_info:
            return Response(status=status.HTTP_200_OK, data={"logo": None, "name": None})
        return Response(
            status=status.HTTP_200_OK,
            data={
                "logo": self.get_logo_url(app_info.logo),
                "name": app_info.name
            }
        )

    @action(methods=["put"], detail=False)
    def update_app_info(self, request, *args, **kwargs):
        self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        app_info = self.app_info_service.update_app_info(
            update_data={
                "name": validated_data.get("name")
            }
        )
        return Response(
            status=status.HTTP_200_OK,
            data={
                "logo": self.get_logo_url(app_info.logo),
                "name": app_info.name
            }
        )

    @action(methods=['get', 'put'], detail=True)
    def app_info_logo(self, request, *args, **kwargs):
        app_info = self.get_object()
        if request.method == "GET":
            logo_url = self.app_info_service.get_app_logo()
            return Response(
                status=status.HTTP_200_OK,
                data={"logo": request.build_absolute_uri(logo_url) if logo_url is not None else logo_url}
            )
        elif request.method == "PUT":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data
            logo = validated_data.get("logo")
            new_logo = self.app_info_service.update_app_logo(
                new_logo=logo
            )

            return Response(
                status=status.HTTP_200_OK,
                data={
                    "logo": request.build_absolute_uri(
                        new_logo) if new_logo is not None else new_logo
                }
            )

    def get_logo_url(self, logo_url):
        if logo_url is not None:
            return self.request.build_absolute_uri(logo_url)
        return None
