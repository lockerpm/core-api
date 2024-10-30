from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from locker_server.api.v1_0.resources.views import ResourcePwdViewSet as ResourceV1PwdViewSet
from locker_server.settings import locker_server_settings
from locker_server.shared.constants.transactions import PLAN_TYPE_PM_ENTERPRISE
from .serializers import CountrySerializer, IndividualPlanSerializer, AutofillKeySerializer


class ResourcePwdViewSet(ResourceV1PwdViewSet):
    """
    Resource ViewSet
    """

    def get_serializer_class(self):
        if self.action == "countries":
            self.serializer_class = CountrySerializer
        elif self.action == "list_individual_plans":
            self.serializer_class = IndividualPlanSerializer
        elif self.action in ['get_autofill_key', 'list_autofill_key']:
            self.serializer_class = AutofillKeySerializer
        return super(ResourcePwdViewSet, self).get_serializer_class()

    @action(methods=["get"], detail=False)
    def countries(self, request, *args, **kwargs):
        countries = self.resource_service.list_countries()
        serializer = self.get_serializer(countries, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(methods=["get"], detail=False)
    def server_type(self, request, *args, **kwargs):
        default_plan = locker_server_settings.DEFAULT_PLAN
        if default_plan == PLAN_TYPE_PM_ENTERPRISE:
            server_type = "enterprise"
        else:
            server_type = "personal"
        app_info = self.app_info_service.get_app_info()
        data = {
            "server_type": server_type
        }
        if app_info is None:
            data.update({
                "logo": None, "name": None
            })
        else:
            data.update({
                "logo": self.request.build_absolute_uri(app_info.logo) if app_info.logo else None,
                "name": app_info.name
            })
        return Response(status=status.HTTP_200_OK, data=data)

    @action(methods=["get"], detail=False)
    def list_enterprise_id(self, request, *args, **kwargs):
        filters = {
            "locked": self.request.query_params.get("locked")
        }
        enterprise_ids = self.enterprise_service.list_enterprise_ids(**filters)
        return Response(status=status.HTTP_200_OK, data=enterprise_ids)

    @action(methods=["get"], detail=False)
    def list_channel(self, request, *args, **kwargs):
        user_channels = [
            {
                "id": "organic",
                "name": "Organic"
            },
            {
                "id": "ads",
                "name": "Ads"
            },
            {
                "id": "affiliate",
                "name": "Affiliate"
            }
        ]
        return Response(status=status.HTTP_200_OK, data=user_channels)

    @action(methods=["get"], detail=False)
    def list_payment_sources(self, request, *args, **kwargs):
        payment_sources = self.resource_service.list_payment_sources()
        return Response(status=status.HTTP_200_OK, data=payment_sources)

    @action(methods=["get"], detail=False)
    def list_individual_plans(self, request, *args, **kwargs):
        individual_plans = self.resource_service.list_all_plans()
        serializer = self.get_serializer(individual_plans, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(methods=["get"], detail=False)
    def list_device(self, request, *args, **kwargs):
        devices = [
            {
                "id": "web",
                "name": "Web app"
            },
            {
                "id": "ios",
                "name": "Mobile IOS"
            },
            {
                "id": "android",
                "name": "Mobile Android"
            },
            {
                "id": "desktop_mac",
                "name": "MacOS"
            },
            {
                "id": "desktop_windows",
                "name": "Windows"
            },
            {
                "id": "desktop_linux",
                "name": "Linux"
            },
            {
                "id": "browser",
                "name": "Extension"
            }
        ]
        return Response(status=status.HTTP_200_OK, data=devices)

    @action(methods=["get"], detail=False)
    def list_user_status(self, request, *args, **kwargs):
        user_statuses = [
            {
                "id": "unverified",
                "name": "Not verified"
            },
            {
                "id": "verified",
                "name": "Verified"
            },
            {
                "id": "created_master_pwd",
                "name": "MP created"
            },
            {
                "id": "deleted",
                "name": "Deleted"
            }
        ]
        return Response(status=status.HTTP_200_OK, data=user_statuses)

    @action(methods=['get'], detail=False)
    def list_autofill_key(self, request, *args, **kwargs):
        autofill_keys = self.resource_service.list_autofill_key()
        serializer = self.get_serializer(autofill_keys, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(methods=['get'], detail=False)
    def get_autofill_key(self, request, *args, **kwargs):
        key = self.kwargs.get('key')
        autofill_key = self.resource_service.get_autofill_by_key(key=key)
        serializer = self.get_serializer(autofill_key, many=False)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
