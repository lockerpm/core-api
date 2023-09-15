from django.contrib.auth.models import AnonymousUser

from locker_server.shared.throttling.app import AppBaseThrottle
from locker_server.shared.general_view import AppGeneralViewSet
from locker_server.api.authentications.token_authentication import TokenAuthentication
from locker_server.api.permissions.app import APIPermission
from locker_server.containers.containers import *
from locker_server.shared.utils.network import get_ip_by_request


class APIBaseViewSet(AppGeneralViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (APIPermission,)
    throttle_classes = (AppBaseThrottle,)
    throttle_scope = 'anonymous'

    auth_service = auth_service
    user_service = user_service
    exclude_domain_service = exclude_domain_service
    cipher_service = cipher_service
    folder_service = folder_service

    team_member_service = team_member_service
    collection_service = collection_service
    sharing_service = sharing_service

    enterprise_service = enterprise_service

    relay_address_service = relay_address_service
    relay_subdomain_service = relay_subdomain_service
    reply_service = reply_service
    def get_throttles(self):
        if self.request.user and not isinstance(self.request.user, AnonymousUser):
            self.throttle_scope = 'user_authenticated'
        else:
            self.throttle_scope = 'anonymous'
        return super(APIBaseViewSet, self).get_throttles()

    def check_pwd_session_auth(self, request):
        # TODO: Check pwd session token
        return True

    def get_client_agent(self):
        return self.request.META.get("HTTP_LOCKER_CLIENT_AGENT") or self.request.META.get("HTTP_USER_AGENT") or ''

    def get_ip(self):
        return self.request.data.get("ip") or get_ip_by_request(request=self.request)

