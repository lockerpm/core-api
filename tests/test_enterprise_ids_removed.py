from django.test import SimpleTestCase
from django.urls import Resolver404, resolve

from locker_server.api.sub.resources.views import ResourcePwdViewSet
from locker_server.api_orm.repositories.enterprise_repository import EnterpriseORMRepository
from locker_server.core.services.enterprise_service import EnterpriseService


class EnterpriseIdsResourceRemovedTestCase(SimpleTestCase):
    """
    The unauthenticated enterprise directory API (WhiteHub #5042) must stay removed
    """

    def test_route_is_not_resolvable(self):
        with self.assertRaises(Resolver404):
            resolve("/v3/resources/enterprise_ids")

    def test_view_action_is_removed(self):
        self.assertFalse(hasattr(ResourcePwdViewSet, "list_enterprise_id"))

    def test_platform_wide_lookup_is_removed(self):
        self.assertFalse(hasattr(EnterpriseService, "list_enterprise_ids"))
        self.assertFalse(hasattr(EnterpriseORMRepository, "list_enterprise_ids"))
