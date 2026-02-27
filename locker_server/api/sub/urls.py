from django.urls import re_path, include
from rest_framework.routers import DefaultRouter

from locker_server.api.sub import views
from locker_server.shared.caching.api_cache_page import LONG_TIME_CACHE

router = DefaultRouter(trailing_slash=False)

urlpatterns = [
    re_path(r'^', include(router.urls))
]

urlpatterns += [
    re_path(r'^resources/countries$', LONG_TIME_CACHE(views.ResourcePwdViewSet.as_view({'get': 'countries'}))),
    re_path(r'^resources/server_type$', views.ResourcePwdViewSet.as_view({'get': 'server_type'})),
    re_path(r'^resources/enterprise_ids$', views.ResourcePwdViewSet.as_view({'get': 'list_enterprise_id'})),
    re_path(r'^resources/channels$', views.ResourcePwdViewSet.as_view({'get': 'list_channel'})),
    re_path(r'^resources/payment_sources$', views.ResourcePwdViewSet.as_view({'get': 'list_payment_sources'})),
    re_path(r'^resources/individual_plans$', views.ResourcePwdViewSet.as_view({'get': 'list_individual_plans'})),
    re_path(r'^resources/devices$', views.ResourcePwdViewSet.as_view({'get': 'list_device'})),
    re_path(r'^resources/users/status$', views.ResourcePwdViewSet.as_view({'get': 'list_user_status'})),
    re_path(r'^resources/cystack_platform/pm/plans$', views.ResourcePwdViewSet.as_view({'get': 'plans'})),
    re_path(r'^resources/cystack_platform/pm/autofill_keys$',
        views.ResourcePwdViewSet.as_view({'get': 'get_autofill_key'})),
    # re_path(r'^resources/cystack_platform/pm/autofill_keys/(?P<key>[0-9a-z-A-Z-_]+)$',
    #     views.ResourcePwdViewSet.as_view({'get': 'get_autofill_key'})),
    re_path(r'^resources/cystack_platform/pm/enterprise/plans$',
        views.ResourcePwdViewSet.as_view({'get': 'enterprise_plans'})),
    re_path(r'^resources/cystack_platform/pm/mail_providers$',
        views.ResourcePwdViewSet.as_view({'get': 'mail_providers'})),
]

""" User """
urlpatterns += [
    re_path(r'^me$', views.UserViewSet.as_view({'get': 'retrieve', 'put': 'update'})),
    re_path(r'^users/logout$', views.UserViewSet.as_view({'post': 'logout'})),
]

""" Factor2 """
urlpatterns += [
    re_path(r'^sso/auth/otp/mail$', views.Factor2ViewSet.as_view({'post': 'auth_otp_mail'})),
    re_path(r'^sso/me/factor2$', views.Factor2ViewSet.as_view({'get': 'factor2', 'post': 'factor2'})),
    re_path(r'^sso/me/factor2/activate_code$', views.Factor2ViewSet.as_view({'post': 'factor2_activate_code'})),
    re_path(r'^sso/me/factor2/activate$', views.Factor2ViewSet.as_view({'post': 'factor2_is_activate'})),
]

""" Notification """
urlpatterns += [
    re_path(r'^notifications$', views.NotificationViewSet.as_view({'get': 'list'})),
    re_path(r'^notifications/read_all$', views.NotificationViewSet.as_view({'get': 'read_all'})),
    re_path(r'^notifications/(?P<id>[0-9a-z-]+)$', views.NotificationViewSet.as_view({'get': 'retrieve', 'put': 'update'})),
]

""" SSO Configuration """
urlpatterns += [
    re_path(r'^sso_configuration/check_exists$', views.SSOConfigurationViewSet.as_view({'get': 'check_exists'})),
    re_path(r'^sso_configuration/get_user$', views.SSOConfigurationViewSet.as_view({'post': 'get_user_by_code'}))

]

""" Teams Management """
urlpatterns += [
    re_path(r'^teams$', views.TeamPwdViewSet.as_view({'get': 'list'}))
]
