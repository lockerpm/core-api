from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from locker_server.api.v1_0 import views
from locker_server.shared.caching.api_cache_page import LONG_TIME_CACHE


router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    url(r'^', include(router.urls))
]

# ------------------------------- Management Command ----------------------------- #
urlpatterns += [

]


# ----------------------------------- Tools ----------------------------- #
urlpatterns += [
    url(r'^tools/breach$', views.ToolPwdViewSet.as_view({'post': 'breach'})),
    url(r'^tools/public/breach$', views.ToolPwdViewSet.as_view({'post': 'public_breach'})),
]


# ----------------------------------- Exclude domains ----------------------------- #
urlpatterns += [
    url(r'^exclude_domains$', views.ExcludeDomainPwdViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^exclude_domains/(?P<pk>[a-z0-9\-]+)$',
        views.ExcludeDomainPwdViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})),
]



