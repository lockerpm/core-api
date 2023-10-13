from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from locker_server.api.v1_admin import views

router = DefaultRouter(trailing_slash=False)
router.register(r'sso_configuration', views.SSOConfigurationViewSet, 'sso_configuration')

urlpatterns = [
    url(r'^', include(router.urls))
]

# ------------------------------- Mail Configuration ----------------------------- #
urlpatterns += [
    url(r'^mail_configuration$', views.AdminMailConfigurationViewSet.as_view({
        'get': 'mail_configuration', 'put': 'update_mail_configuration', 'delete': 'destroy_mail_configuration'
    })),
    url(r'^mail_configuration/test$', views.AdminMailConfigurationViewSet.as_view({'post': 'send_test_mail'}))
]
