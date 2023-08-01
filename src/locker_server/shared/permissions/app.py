from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission


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
