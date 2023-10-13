import json

from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.decorators import action

from locker_server.api.api_base_view import APIBaseViewSet

from locker_server.core.exceptions.sso_configuration_exception import SSOConfigurationIdentifierExistedException, \
    SSOConfigurationDoesNotExistException
from locker_server.core.exceptions.user_exception import UserDoesNotExistException
from .serializers import *
from locker_server.api.permissions.locker_permissions.sso_configuration_permissions import SSOConfigurationPermission


class SSOConfigurationViewSet(APIBaseViewSet):
    permission_classes = (SSOConfigurationPermission,)
    http_method_names = ["options", "head", "get", "post", "put", "delete"]
    lookup_value_regex = r'[0-9a-z-]+'

    def get_throttles(self):
        return super().get_throttles()

    def get_serializer_class(self):
        if self.action == "list":
            self.serializer_class = ListSSOConfigurationSerializer
        elif self.action == "retrieve":
            self.serializer_class = DetailSSOConfigurationSerializer
        elif self.action == "update":
            self.serializer_class = UpdateSSOConfigurationSerializer
        elif self.action == "create":
            self.serializer_class = CreateSSOConfigurationSerializer
        elif self.action == "get_user_from_sso":
            self.serializer_class = RetrieveUserSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        sso_configurations = self.sso_configuration_service.list_sso_configurations(**{
            "created_by_id": user.user_id
        })
        return sso_configurations

    def get_object(self):
        try:
            sso_configuration = self.sso_configuration_service.get_sso_configuration(
                sso_configuration_id=self.kwargs.get("pk")
            )
            self.check_object_permissions(request=self.request, obj=sso_configuration)
            return sso_configuration
        except SSOConfigurationDoesNotExistException:
            raise NotFound

    def list(self, request, *args, **kwargs):
        paging_param = self.request.query_params.get("paging", "1")
        page_size_param = self.check_int_param(self.request.query_params.get("size", 10))
        if paging_param == "0":
            self.pagination_class = None
        else:
            self.pagination_class.page_size = page_size_param if page_size_param else 10
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        sso_configuration = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        try:
            updated_sso_configuration = self.sso_configuration_service.update_sso_configuration(
                sso_configuration_id=sso_configuration.sso_configuration_id,
                sso_config_update_data={
                    "sso_provider_id": validated_data.get("sso_provider"),
                    "sso_provider_options": json.dumps(validated_data.get("sso_provider_options") or {}),
                    "enabled": validated_data.get("enabled"),
                    "identifier": validated_data.get("identifier"),
                }
            )
        except SSOConfigurationIdentifierExistedException:
            raise ValidationError(detail={"identifier": ["SSO with this identifier already exists"]})
        except SSOConfigurationDoesNotExistException:
            raise NotFound
        serializer = DetailSSOConfigurationSerializer(updated_sso_configuration, many=False)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        try:
            new_sso_configuration = self.sso_configuration_service.create_sso_configuration(
                user_id=user.user_id,
                sso_config_create_data={
                    "sso_provider_id": validated_data.get("sso_provider"),
                    "sso_provider_options": json.dumps(validated_data.get("sso_provider_options") or {}),
                    "enabled": validated_data.get("enabled"),
                    "identifier": validated_data.get("identifier"),
                    "created_by_id": user.user_id
                }
            )
        except SSOConfigurationIdentifierExistedException:
            raise ValidationError(detail={"identifier": ["SSO with this identifier already exists"]})
        except UserDoesNotExistException:
            raise NotFound
        return Response(status=status.HTTP_201_CREATED, data={"id": new_sso_configuration.sso_configuration_id})

    @action(methods=["get"], detail=False)
    def get_sso_config(self, request, *args, **kwargs):
        sso_identifier = request.query_params.get("sso_identifier")
        try:
            sso_configuration = self.sso_configuration_service.get_sso_configuration_by_identifier(
                identifier=sso_identifier
            )
        except SSOConfigurationDoesNotExistException:
            raise NotFound
        serializer = DetailSSOConfigurationSerializer(sso_configuration, many=False)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(methods=["post"], detail=False)
    def get_user_from_sso(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        try:
            user_data = self.sso_configuration_service.get_user_from_sso_configuration(
                sso_identifier=validated_data.get("sso_identifier"),
                auth_token=validated_data.get("auth_token")
            )
        except SSOConfigurationDoesNotExistException:
            raise NotFound
        return Response(status=status.HTTP_200_OK, data={"user": user_data})
