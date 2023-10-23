from rest_framework.exceptions import NotFound

from locker_server.core.exceptions.enterprise_exception import EnterpriseDoesNotExistException

from .serializers import *
from locker_server.api.api_base_view import APIBaseViewSet

from locker_server.api.permissions.admin_permissions.admin_enterprise_member_permission import \
    AdminEnterpriseMemberPermission


class AdminEnterpriseMemberViewSet(APIBaseViewSet):
    permission_classes = (AdminEnterpriseMemberPermission,)
    lookup_value_regex = r'[0-9a-z\-]+'
    http_method_names = ["head", "options", "get", "post", "put", "delete"]

    def get_serializer_class(self):
        if self.action == "list":
            self.serializer_class = ListMemberSerializer
        return super().get_serializer_class()

    def get_enterprise(self):
        try:
            enterprise = self.enterprise_service.get_enterprise_by_id(
                enterprise_id=self.kwargs.get("enterprise_id")
            )
            self.check_object_permissions(request=self.request, obj=enterprise)
            return enterprise
        except EnterpriseDoesNotExistException:
            raise NotFound

    def get_queryset(self):
        enterprise = self.get_enterprise()
        members = self.enterprise_member_service.list_enterprise_members(**{
            "enterprise_id": enterprise.enterprise_id
        })

        return members

    def list(self, request, *args, **kwargs):
        paging_param = self.request.query_params.get("paging", "1")
        page_size_param = self.check_int_param(self.request.query_params.get("size", 10))
        if paging_param == "0":
            self.pagination_class = None
        else:
            self.pagination_class.page_size = page_size_param if page_size_param else 10

        return super().list(request, *args, **kwargs)
