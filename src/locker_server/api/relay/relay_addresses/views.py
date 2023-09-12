from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.relay_address_permission import RelayAddressPermission
from locker_server.core.exceptions.relay_address_exception import RelayAddressDoesNotExistException

from .serializers import *


class RelayAddressViewSet(APIBaseViewSet):
    permission_classes = (RelayAddressPermission,)
    http_method_names = ["head", "options", "get", "post", "put", "delete"]
    lookup_value_regex = r'[0-9]+'

    def get_throttles(self):
        return super().get_throttles()

    def get_serializer_class(self):
        if self.action == 'list':
            self.serializer_class = ListRelayAddressSerializer
        elif self.action == 'retrieve':
            self.serializer_class = DetailRelayAddressSerializer
        elif self.action == "update":
            self.serializer_class = UpdateRelayAddressSerializer
        elif self.action == 'create':
            self.serializer_class = CreateRelayAddressSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        relay_addresses = self.relay_address_service.list_user_relay_addresses(user_id=user.user_id)
        return relay_addresses

    def get_object(self):
        user = self.request.user
        try:
            relay_address = self.relay_service.objects.get(id=self.kwargs.get("pk"), user=self.request.user)
            if relay_address.user.user_id != user.user_id:
                raise NotFound
            self.check_object_permissions(request=self.request, obj=relay_address)
            return relay_address
        except RelayAddressDoesNotExistException:
            raise NotFound

    def get_subdomain(self):
        user = self.request.user
        # TODO: using relay_subdomains service to get first subdomain for this function
        subdomain = user.relay_subdomains.filter(is_deleted=False, domain_id=DEFAULT_RELAY_DOMAIN).first()
        return subdomain

    def allow_relay_premium(self) -> bool:
        user = self.request.user
        current_plan = self.user_repository.get_current_plan(user=user, scope=settings.SCOPE_PWD_MANAGER)
        plan_obj = current_plan.get_plan_obj()
        return plan_obj.allow_relay_premium() or user.is_active_enterprise_member()

    def list(self, request, *args, **kwargs):
        paging_param = self.request.query_params.get("paging", "1")
        size_param = self.request.query_params.get("size", 50)
        page_size_param = self.check_int_param(size_param)
        if paging_param == "0":
            self.pagination_class = None
        else:
            self.pagination_class.page_size = page_size_param or 50
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data or {}
        allow_relay_premium = self.allow_relay_premium()
        # Check the limit of addresses
        validated_data.update({"allow_relay_premium": allow_relay_premium})
        # Check the user uses subdomain or not
        if user.use_relay_subdomain is True and allow_relay_premium is True:
            subdomain = self.get_subdomain()
            validated_data.update({"subdomain_id": subdomain.relay_subdomain_id})
        try:
            new_relay_address = self.relay_address_service.create_relay_service(
                user_id=user.user_id,
                relay_address_create_data=validated_data
            )
        except UserDoesNotExistException:
            raise ValidationError({"non_field_errors": [gen_error("8000")]})
        except RelayAddressReachedException:
            raise ValidationError({"non_field_errors": [gen_error("8000")]})
        return Response(status=201, data=DetailRelayAddressSerializer(new_relay_address).data)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        relay_address = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        try:
            updated_relay_address = self.relay_address_service.update_relay_address(
                user_id=user.user_id,
                relay_address=relay_address,
                relay_address_update_data=validated_data
            )
        except:
            pass
        return Response(status=200, data={"id": relay_address.id})

    def destroy(self, request, *args, **kwargs):
        relay_address = self.get_object()
        # Create deleted address
        relay_address.delete_permanently()
        return Response(status=204)

    @action(methods=["put"], detail=True)
    def block_spam(self, request, *args, **kwargs):
        relay_address = self.get_object()
        allow_relay_premium = self.allow_relay_premium()
        if allow_relay_premium is False:
            raise ValidationError({"non_field_errors": [gen_error("7002")]})
        relay_address.block_spam = not relay_address.block_spam
        relay_address.save()
        return Response(status=200, data={"id": relay_address.id, "block_spam": relay_address.block_spam})

    @action(methods=["put"], detail=True)
    def enabled(self, request, *args, **kwargs):
        relay_address = self.get_object()
        relay_address.enabled = not relay_address.enabled
        relay_address.save()
        return Response(status=200, data={"id": relay_address.id, "enabled": relay_address.enabled})
