from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from locker_server.api.sso import views

router = DefaultRouter(trailing_slash=False)
router.register(r'configurations', views.SSOConfigurationViewSet, 'configurations')

urlpatterns = [
    url(r'^', include(router.urls))
]

# ------------------------------- Management Command ----------------------------- #
urlpatterns += [

]

# ------------------------------- Resources ----------------------------- #
urlpatterns += [

]
