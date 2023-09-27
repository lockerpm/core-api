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


# # ------------------------------- Resources ----------------------------- #
# urlpatterns += [
#     url(r'^resources/plans$', views.ResourcePwdViewSet.as_view({'get': 'plans'})),
#     url(r'^resources/enterprise/plans$', views.ResourcePwdViewSet.as_view({'get': 'enterprise_plans'})),
# ]

