from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from locker_server.api.v1_admin import views


router = DefaultRouter(trailing_slash=False)
router.register(r'enterprises', views.AdminEnterpriseViewSet, "admin_enterprise")
router.register(
    r'enterprises/(?P<enterprise_id>[0-9a-z-]+)/members', views.AdminEnterpriseMemberViewSet,
    "admin_enterprise_member"
)

urlpatterns = [
    re_path(r'^', include(router.urls))
]


# ------------------------------- Mail Configuration ----------------------------- #
urlpatterns += [
    re_path(r'^mail_configuration$', views.AdminMailConfigurationViewSet.as_view({
        'get': 'mail_configuration', 'put': 'update_mail_configuration', 'delete': 'destroy_mail_configuration'
    })),
    re_path(r'^mail_configuration/test$', views.AdminMailConfigurationViewSet.as_view({'post': 'send_test_mail'}))
]


# ------------------------------- SSO Configuration ----------------------------- #
urlpatterns += [
    re_path(r'^sso_configuration$', views.AdminSSOConfigurationViewSet.as_view({
        'get': 'sso_configuration', 'put': 'update_sso_configuration', 'delete': 'destroy_sso_configuration'
    }))
]


# ------------------------------- App Info ----------------------------- #
urlpatterns += [
    re_path(r'^app_info$', views.AdminAppInfoViewSet.as_view({
        'get': 'app_info', 'put': 'update_app_info',
    })),
    re_path(r'^app_info/logo$', views.AdminAppInfoViewSet.as_view({
        'get': 'app_info_logo', 'put': 'app_info_logo',
    })),
]
