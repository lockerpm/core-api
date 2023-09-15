import json
import os

from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from slocker_server.api.api_base_view import APIBaseViewSet
from locker_server.core.exceptions.relay_exceptions.relay_subdomain_exception import *
from locker_server.core.exceptions.user_exception import UserDoesNotExistException
from .serializers import *
from locker_server.api.permissions.relay_permissions.relay_subdomain_permission import RelaySubdomainPermission


class RelaySubdomainViewSet(APIBaseViewSet):
    permission_classes = (RelaySubdomainPermission,)
    http_method_names = ["head", "options", "get", "post", "put", "delete"]
    lookup_value_regex = r'[0-9]+'

    def get_throttles(self):
        return super().get_throttles()

    def get_serializer_class(self):
        if self.action == 'list':
            self.serializer_class = ListRelaySubdomainsSerializer
        elif self.action == 'retrieve':
            self.serializer_class = DetailRelaySubdomainSerializer
        elif self.action == "update":
            self.serializer_class = UpdateRelaySubdomainSerializer
        elif self.action == 'create':
            self.serializer_class = CreateRelaySubdomainSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        relay_subdomains = self.relay_subdomain_service.list_user_relay_subdomains(user_id=user.user_id, **{
            "is_deleted": False
        })
        return relay_subdomains

    def get_object(self):
        user = self.request.user
        try:
            relay_subdomain = self.relay_subdomain_service.get_relay_subdomain_by_id(
                relay_subdomain_id=self.kwargs.get("pk")
            )
            if relay_subdomain.user.user_id != user.user_id:
                raise NotFound
            self.check_object_permissions(request=self.request, obj=relay_subdomain)
            return relay_subdomain
        except RelaySubdomainDoesNotExistException:
            raise NotFound

    def allow_relay_premium(self) -> bool:
        user = self.request.user
        current_plan = self.user_service.get_current_plan(user=user)
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
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data or {}
        allow_relay_premium = self.allow_relay_premium()
        if not allow_relay_premium:
            raise ValidationError({"non_field_errors": [gen_error("7002")]})
        try:
            new_relay_subdomain = self.relay_subdomain_service.create_relay_subdomain(
                user_id=user.user_id,
                relay_subdomain_create_data=validated_data
            )
        except UserDoesNotExistException:
            raise NotFound
        except MaxRelaySubdomainReachedException:
            raise ValidationError({"non_field_errors": [gen_error("8001")]})
        except RelaySubdomainExistedException:
            raise ValidationError(detail={"subdomain": [
                "This subdomain is used. Try another subdomain",
                "Tên miền phụ này đã được sử dụng. Hãy thử lại với tên miền phụ khác"
            ]})
        except RelaySubdomainInvalidException:
            raise ValidationError(detail={"subdomain": [
                "This subdomain is not valid (has black words, blocked words, etc...)",
                "Tên miền phụ này có chứa từ khóa không hợp lệ"
            ]})
        if os.getenv("PROD_ENV") == "prod":
            action_msg = {'action': 'create',
                          'domain': f"{new_relay_subdomain.subdomain}.{new_relay_subdomain.domain.relay_domain_id}"}
            create_msg = {'Type': 'DomainIdentity', 'Message': json.dumps(action_msg)}
            #TODO: sqs service
            sqs_service.send_message(message_body=json.dumps(create_msg))

        return Response(status=status.HTTP_201_CREATED,
                        data={"id": new_relay_subdomain.relay_subdomain_id, "subdomain": new_relay_subdomain.subdomain})

    def update(self, request, *args, **kwargs):
        user = self.request.user
        relay_subdomain = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        old_subdomain = relay_subdomain.subdomain
        subdomain = validated_data.get("subdomain")
        if old_subdomain != subdomain:
            try:
                updated_relay_subdomain = self.relay_subdomain_service.update_relay_subdomain(
                    user_id=user.user_id,
                    relay_subdomain_id=relay_subdomain.relay_subdomain_id,
                    relay_subdomain_update_data=validated_data
                )
                # Delete all relay addresses of this subdomain
                self.relay_address_service.delete_relay_addresses_by_subdomain_id(
                    subdomain_id=updated_relay_subdomain.relay_subdomain_id
                )
                # Create deletion SQS job
                if os.getenv("PROD_ENV") == "prod":
                    action_delete_msg = {'action': 'delete',
                                         'domain': f"{old_subdomain}.{updated_relay_subdomain.domain.relay_domain_id}"}
                    delete_msg = {'Type': 'DomainIdentity', 'Message': json.dumps(action_delete_msg)}
                    sqs_service.send_message(message_body=json.dumps(delete_msg))
                # Save subdomain object as deleted
                self.relay_subdomain_service.create_relay_subdomain(
                    user_id=user.user_id,
                    relay_subdomain_create_data={
                        "subdomain": old_subdomain,
                        "is_deleted": True
                    }
                )
                # Send creation job to SQS
                if os.getenv("PROD_ENV") == "prod":
                    action_create_msg = {'action': 'create',
                                         'domain': f"{subdomain}.{updated_relay_subdomain.domain.relay_domain_id}"}
                    create_msg = {'Type': 'DomainIdentity', 'Message': json.dumps(action_create_msg)}
                    #TODO: handle sqs_service
                    sqs_service.send_message(message_body=json.dumps(create_msg))
            except RelaySubdomainAlreadyUsedException:
                raise ValidationError(detail={"subdomain": [
                    "This subdomain is used. Try another subdomain",
                    "Tên miền phụ này đã được sử dụng. Hãy thử lại với tên miền phụ khác"
                ]})
            except RelaySubdomainDoesNotExistException:
                raise NotFound
            except RelaySubdomainInvalidException:
                raise ValidationError(detail={"subdomain": [
                    "This subdomain is not valid (has black words, blocked words, etc...)",
                    "Tên miền phụ này có chứa từ khóa không hợp lệ"
                ]})
        return Response(status=status.HTTP_200_OK, data={"id": relay_subdomain.relay_subdomain_id})

    def destroy(self, request, *args, **kwargs):
        relay_subdomain = self.get_object()
        try:
            deleted_relay_subdomain = self.relay_subdomain_service.soft_delete_relay_subdomain(
                relay_subdomain=relay_subdomain
            )
            # Delete all relay addresses of this subdomain
            self.relay_address_service.delete_relay_addresses_by_subdomain_id(
                subdomain_id=relay_subdomain.relay_subdomain_id
            )
            # Create deletion SQS job
            if os.getenv("PROD_ENV") == "prod":
                action_delete_msg = {'action': 'delete',
                                     'domain': f"{deleted_relay_subdomain.subdomain}.{deleted_relay_subdomain.domain.relay_domain_id}"}
                delete_msg = {'Type': 'DomainIdentity', 'Message': json.dumps(action_delete_msg)}
                sqs_service.send_message(message_body=json.dumps(delete_msg))
        except RelaySubdomainDoesNotExistException:
            raise NotFound
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["get", "put"], detail=False)
    def use_subdomain(self, request, *args, **kwargs):
        user = request.user
        if request.method == "GET":
            return Response(status=status.HTTP_200_OK, data={"use_relay_subdomain": user.use_relay_subdomain})

        elif request.method == "PUT":
            allow_relay_premium = self.allow_relay_premium()
            if not allow_relay_premium:
                raise ValidationError({"non_field_errors": [gen_error("7002")]})
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data
            use_relay_subdomain = validated_data.get("use_relay_subdomain")
            try:
                updated_user = self.user_service.update_user(
                    user_id=user.userid,
                    user_update_data={
                        'user_relay_subdomain': use_relay_subdomain
                    }
                )
            except UserDoesNotExistException:
                raise NotFound
            return Response(status=status.HTTP_200_OK, data={"use_relay_subdomain": updated_user.use_relay_subdomain})
