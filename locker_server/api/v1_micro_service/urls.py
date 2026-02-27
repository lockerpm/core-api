from django.urls import re_path, include
from rest_framework.routers import DefaultRouter

from locker_server.api.v1_micro_service import views


router = DefaultRouter(trailing_slash=False)
router.register(r'users', views.UserViewSet, "users")


urlpatterns = [
    re_path(r'^', include(router.urls))
]

# ----------------------- Payments --------------------------- #
urlpatterns += [

]

