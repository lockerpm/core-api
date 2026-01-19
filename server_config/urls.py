from django.conf import settings
from django.urls import include, re_path
from django.conf.urls.static import static

urlpatterns = [
    re_path(r'^admin/', include('locker_server.api.v1_admin.urls')),
    re_path(r'^v3/', include('locker_server.api.sub.urls')),
    re_path(r'^v3/pm/ms/', include('locker_server.api.v1_micro_service.urls')),
    re_path(r'^v3/cystack_platform/pm/', include('locker_server.api.v1_0.urls')),
    re_path(r'^v3/cystack_platform/pm/enterprises/', include('locker_server.api.v1_enterprise.urls')),
    # url(r'^v3/cystack_platform/relay/', include('locker_server.api.relay.urls')),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
