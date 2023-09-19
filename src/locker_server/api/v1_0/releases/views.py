from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from .serializers import *
from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.release_permission import ReleasePermission
from locker_server.shared.constants.device_type import CLIENT_ID_DESKTOP


class ReleaseViewSet(APIBaseViewSet):
    permission_classes = (ReleasePermission,)
    http_method_names = ["head", "options", "get", "post"]

    def get_serializer_class(self):
        if self.action == "new":
            self.serializer_class = NewReleaseSerializer
        elif self.action == "current":
            self.serializer_class = NextReleaseSerializer
        return super().get_serializer_class()

    @action(methods=["get", "post"], detail=False)
    def current(self, request, *args, **kwargs):
        if request.method == "GET":
            client_id = self.request.query_params.get("client_id", CLIENT_ID_DESKTOP)
            environment = self.request.query_params.get("environment", RELEASE_ENVIRONMENT_PROD)

            latest_release = self.release_service.get_latest_release(
                client_id=client_id,
                environment=environment
            )

            if not latest_release:
                version = "1.0.0"
            else:
                version = latest_release.version
            data = {
                "version": version,
                "environment": environment
            }
            return Response(status=status.HTTP_200_OK, data=data)

        elif request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data
            client_id = validated_data.get("client_id")
            environment = validated_data.get("environment")
            next_release = self.release_service.create_next_release(client_id=client_id, environment=environment)
            if not next_release:
                version = "1.0.0"
            else:
                version = next_release.version
            data = {
                "version": version,
                "environment": environment
            }
            return Response(status=status.HTTP_200_OK, data=data)

    @action(methods=["post"], detail=False)
    def new(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        success_build = validated_data.get("build")
        client_id = validated_data.get("client_id")
        environment = validated_data.get("environment")

        if not success_build:
            data = {
                "build": success_build,
                "version": None,
                "environment": environment
            }
            return Response(status=status.HTTP_200_OK, data=data)
        next_release = self.release_service.create_next_release(client_id=client_id, environment=environment)
        if not next_release:
            version = "1.0.0"
        else:
            version = next_release.version
        data = {
            "version": version,
            "environment": environment
        }
        return Response(status=status.HTTP_200_OK, data=data)

    @action(methods=["get"], detail=False)
    def current_version(self, request, *args, **kwargs):
        client_id = self.request.query_params.get("client_id", CLIENT_ID_DESKTOP)
        environment = self.request.query_params.get("environment", RELEASE_ENVIRONMENT_PROD)
        latest_release = self.release_service.get_latest_release(
            client_id=client_id,
            environment=environment
        )

        if not latest_release:
            version = "1.0.0"
        else:
            version = latest_release.version
        data = {
            "version": version,
            "environment": environment
        }
        return Response(status=status.HTTP_200_OK, data=data)
