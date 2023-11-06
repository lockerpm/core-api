from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.release_pwd_permission import ReleasePwdPermission
from locker_server.shared.constants.device_type import CLIENT_ID_DESKTOP
from locker_server.shared.constants.release import RELEASE_ENVIRONMENT_PROD
from .serializers import NewReleaseSerializer, NextReleaseSerializer, ListReleaseSerializer, DetailReleaseSerializer


class ReleasePwdViewSet(APIBaseViewSet):
    permission_classes = (ReleasePwdPermission,)
    http_method_names = ["head", "options", "get", "post"]

    def get_serializer_class(self):
        if self.action == "new":
            self.serializer_class = NewReleaseSerializer
        elif self.action == "list":
            self.serializer_class = ListReleaseSerializer
        elif self.action == "retrieve":
            self.serializer_class = DetailReleaseSerializer
        elif self.action == "current":
            self.serializer_class = NextReleaseSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        releases = self.release_service.list_releases(**{
            "client_id": self.request.query_params.get("client_id"),
            "environment": self.request.query_params.get("environment")
        })
        return releases

    def get_object(self):
        client_id = self.kwargs.get("client_id")
        version = self.kwargs.get("version")
        release = self.release_service.get_release(
            client_id=client_id,
            version=version
        )
        if release is None:
            raise NotFound
        return release

    def list(self, request, *args, **kwargs):
        paging_param = self.request.query_params.get("paging", "0")
        page_size_param = self.check_int_param(self.request.query_params.get("size", 50))
        if paging_param == "0":
            self.pagination_class = None
        else:
            self.pagination_class.page_size = page_size_param if page_size_param else 50
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(methods=["get", "post"], detail=False)
    def current(self, request, *args, **kwargs):
        if request.method == "GET":
            client_id = self.request.query_params.get("client_id", CLIENT_ID_DESKTOP)
            environment = self.request.query_params.get("environment", RELEASE_ENVIRONMENT_PROD)
            latest_release = self.release_service.get_latest_release(
                client_id=client_id,
                environment=environment
            )
            version = latest_release.version if latest_release else "1.0.0"
            data = {
                "version": version,
                "environment": environment,
                "checksum": latest_release.get_checksum()
            }
            return Response(status=status.HTTP_200_OK, data=data)

        elif request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data
            client_id = validated_data.get("client_id")
            environment = validated_data.get("environment")
            next_release = self.release_service.generate_next_release(
                client_id=client_id,
                environment=environment,
            )
            if not next_release:
                return Response(
                    status=status.HTTP_200_OK,
                    data={"version": "1.0.0", "environment": environment}
                )
            return Response(status=status.HTTP_200_OK, data={
                "version": next_release.version,
                "environment": next_release.environment,
            })

    @action(methods=["post"], detail=False)
    def new(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        success_build = validated_data.get("build")
        client_id = validated_data.get("client_id")
        environment = validated_data.get("environment")
        checksum = validated_data.get("checksum")
        if not success_build:
            data = {
                "build": success_build,
                "version": None,
                "environment": environment
            }
            return Response(status=status.HTTP_200_OK, data=data)
        next_release = self.release_service.create_next_release(
            client_id=client_id,
            environment=environment,
            checksum=checksum
        )
        if not next_release:
            version = "1.0.0"
        else:
            version = next_release.version
        data = {
            "version": version,
            "environment": environment,
            "checksum": next_release.get_checksum() if next_release else None
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
            "environment": environment,
            "checksum": latest_release.get_checksum() if latest_release else None
        }
        return Response(status=status.HTTP_200_OK, data=data)
