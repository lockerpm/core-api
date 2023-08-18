from django.contrib.auth.models import AnonymousUser

from locker_server.shared.throttling.app import AppBaseThrottle
from locker_server.shared.general_view import AppGeneralViewSet
from locker_server.api.authentications.token_authentication import TokenAuthentication
from locker_server.api.permissions.app import APIPermission
from locker_server.containers.containers import *


class APIBaseViewSet(AppGeneralViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (APIPermission,)
    throttle_classes = (AppBaseThrottle,)
    throttle_scope = 'anonymous'

    auth_service = auth_service
    user_service = user_service

    def get_throttles(self):
        if self.request.user and not isinstance(self.request.user, AnonymousUser):
            self.throttle_scope = 'user_authenticated'
        else:
            self.throttle_scope = 'anonymous'
        return super(APIBaseViewSet, self).get_throttles()

    def check_pwd_session_auth(self, request):
        # TODO: Check pwd session token
        return True
