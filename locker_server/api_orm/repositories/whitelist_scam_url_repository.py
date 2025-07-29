from typing import Optional, List, NoReturn

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models import WhitelistScamUrlORM
from locker_server.core.entities.scam_setting.whitelist_scam_url import WhitelistScamUrl
from locker_server.core.repositories.whitelist_scam_url import WhitelistScamUrlRepository
from locker_server.shared.utils.app import now

ModelParser = get_model_parser()


class WhitelistScamUrlORMRepository(WhitelistScamUrlRepository):
    @staticmethod
    def _get_wl_scam_url(scam_url_id: str) -> WhitelistScamUrlORM:
        try:
            wl_orm = WhitelistScamUrlORM.objects.get(id=scam_url_id)
            return wl_orm
        except WhitelistScamUrlORM.DoesNotExist:
            return None

    @staticmethod
    def filter_whitelist_urls(wl_scam_urls_orm, **filter):
        q_param = filter.get("q")
        if q_param:
            wl_scam_urls_orm = wl_scam_urls_orm.filter(url__icontains=q_param)

        return wl_scam_urls_orm

    def list_wl_scam_urls(self, user_id: int, **filters) -> List[WhitelistScamUrl]:
        wl_urls = WhitelistScamUrlORM.objects.filter(user_id=user_id)
        wl_urls = self.filter_whitelist_urls(wl_urls, **filters)
        wl_urls.select_related('user').order_by('created_at')
        return [
            ModelParser.notification_parser().parse_whitelist_url(
                wl_url
            )
            for wl_url in wl_urls
        ]

    def get_wl_scam_url_by_id(self, wl_scam_url_id: str) -> Optional[WhitelistScamUrl]:
        wl_url_orm = self._get_wl_scam_url(wl_scam_url_id)
        if wl_url_orm:
            return ModelParser.notification_parser().parse_whitelist_url(wl_url_orm)
        return None

    def get_by_url(self, user_id, url) -> Optional[WhitelistScamUrl]:
        try:
            wl_url_orm = WhitelistScamUrlORM.objects.get(url=url, user_id=user_id)
            return ModelParser.notification_parser().parse_whitelist_url(wl_url_orm)
        except WhitelistScamUrlORM.DoesNotExist:
            return None

    def create_wl_scam_url(self, **create_data) -> WhitelistScamUrl:
        wl_url_orm, is_created = WhitelistScamUrlORM.objects.get_or_create(
            user_id=create_data.get("user_id"),
            url=create_data.get("url"),
            defaults={
                "url": create_data.get("url"),
                "user_id": create_data.get("user_id"),
                "created_at": create_data.get("created_at", now()),
                "updated_at": create_data.get("updated_at", now()),
            })
        if not is_created:
            wl_url_orm.updated_at = now()

        wl_url_orm.save()
        return ModelParser.notification_parser().parse_whitelist_url(wl_url_orm)

    def update_wl_scam_url(self, wl_scam_url_id: str, **update_data) -> Optional[WhitelistScamUrl]:

        wl_url_orm = self._get_wl_scam_url(wl_scam_url_id)
        if wl_url_orm:
            wl_url_orm.url = update_data.get('url', wl_url_orm.url)
            wl_url_orm.updated_at = update_data.get('updated_at', now())
            wl_url_orm.save()
            return ModelParser.notification_parser().parse_whitelist_url(wl_url_orm)
        return None

    def delete_wl_scam_url(self, wl_scam_url_id: str) -> bool:
        wl_url_orm = self._get_wl_scam_url(wl_scam_url_id)
        if wl_url_orm:
            wl_url_orm.delete()
            return True
        return False
