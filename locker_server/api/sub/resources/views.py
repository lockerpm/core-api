from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from locker_server.api.v1_0.resources.views import ResourcePwdViewSet as ResourceV1PwdViewSet
from locker_server.settings import locker_server_settings
from locker_server.shared.constants.transactions import PLAN_TYPE_PM_ENTERPRISE
from .serializers import CountrySerializer


class ResourcePwdViewSet(ResourceV1PwdViewSet):
    """
    Resource ViewSet
    """

    def get_serializer_class(self):
        if self.action == "countries":
            self.serializer_class = CountrySerializer
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
                "id": "organic"
            },
            {
                "id": "ads"
            },
            {
                "id": "affiliate"
            }
        ]
        return Response(status=status.HTTP_200_OK, data=user_channels)

    @action(methods=["get"], detail=False)
    def list_saas_market(self, request, *args, **kwargs):
        saas_markets = self.payment_service.list_saas_market()
        return Response(status=status.HTTP_200_OK, data=saas_markets)
