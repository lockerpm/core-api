from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission

from locker_server.containers.containers import auth_service
from django.conf import settings

CACHE_ROLE_PERMISSION_PREFIX = "cs_role_permission_"


class AppBasePermission(BasePermission):
    scope = 'general'

    def has_permission(self, request, view):
        return self.is_auth(request)

    def has_object_permission(self, request, view, obj):
        return super(AppBasePermission, self).has_object_permission(request, view, obj)

    @staticmethod
    def is_auth(request):
        if request.user and (request.auth is not None):
            return False if isinstance(request.user, AnonymousUser) else True
        return False

    def is_admin(self, request):
        if self.is_auth(request):
            token = request.auth
            payload = auth_service.decode_token(token, secret=settings.SECRET_KEY)
            check_admin = payload.get("is_admin") if payload is not None else False
            if (check_admin == "1") or (check_admin == 1) or (check_admin is True):
                return True
        return False
