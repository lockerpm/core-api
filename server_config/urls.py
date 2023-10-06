from django.conf.urls import url, include


urlpatterns = [
    url(r'^v3/', include('locker_server.api.sub.urls')),
    url(r'^v3/pm/ms/', include('locker_server.api.v1_micro_service.urls')),
    url(r'^v3/cystack_platform/pm/', include('locker_server.api.v1_0.urls')),
    # url(r'^v3/cystack_platform/pm/enterprises/', include('api.v1_enterprise.urls')),
    # url(r'^v3/cystack_platform/relay/', include('api.relay.urls')),

]