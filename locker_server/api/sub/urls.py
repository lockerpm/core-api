from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from locker_server.api.sub import views
from locker_server.shared.caching.api_cache_page import LONG_TIME_CACHE


router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    url(r'^', include(router.urls))
]


urlpatterns += [
    url(r'^resources/countries$', LONG_TIME_CACHE(views.ResourcePwdViewSet.as_view({'get': 'countries'}))),
    url(r'^resources/cystack_platform/pm/plans$', views.ResourcePwdViewSet.as_view({'get': 'plans'})),
    url(r'^resources/cystack_platform/pm/enterprise/plans$',
        views.ResourcePwdViewSet.as_view({'get': 'enterprise_plans'})),
]
