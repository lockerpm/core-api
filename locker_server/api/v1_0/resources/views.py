from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from .serializers import PMPlanSerializer


class ResourcePwdViewSet(APIBaseViewSet):
    permission_classes = ()
    http_method_names = ["head", "options", "get"]

    def get_serializer_class(self):
        if self.action in ["plans", "enterprise_plans"]:
            self.serializer_class = PMPlanSerializer
        return super(ResourcePwdViewSet, self).get_serializer_class()

    @action(methods=["get"], detail=False)
    def plans(self, request, *args, **kwargs):
        personal_plan = self.resource_service.list_personal_plans()
        serializer = self.get_serializer(personal_plan, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(methods=["get"], detail=False)
    def enterprise_plans(self, request, *args, **kwargs):
        enterprise_plans = self.resource_service.list_enterprise_plans()
        serializer = self.get_serializer(enterprise_plans, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
