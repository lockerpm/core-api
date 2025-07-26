from typing import Optional, List, NoReturn

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models import ScamSettingORM
from locker_server.core.entities.scam_setting.scam_setting import ScamSetting
from locker_server.core.repositories.user_scam_setting_repository import ScamSettingRepository
from locker_server.shared.utils.app import now

ModelParser = get_model_parser()


class ScamSettingORMRepository(ScamSettingRepository):
    def _list_scam_setting_orm(self, user_id: str, **filters):
        scam_settings_orm = ScamSettingORM.objects.filter(
            user_id=user_id, category__enabled=True
        ).select_related("category").order_by('category_id')
        return scam_settings_orm

    def list_user_scam_settings(self, user_id: int, **filters) -> List[ScamSetting]:
        scam_settings_orm = self._list_scam_setting_orm(user_id, **filters)
        return [
            ModelParser.notification_parser().parse_user_scam_setting(
                scam_setting_orm,
            )
            for scam_setting_orm in scam_settings_orm
        ]

    def check_user_scam_settings(self, user_id: int) -> bool:
        pass

    def get_user_scam_setting(self, category_id: str, user_ids: List[int]) -> List[int]:
        pass

    def get_user_mail(self, category_id: str, user_ids: List[int]) -> List[int]:
        pass

    def get_user_scam_by_category_id(self, user_id: int, category_id: str) -> Optional[ScamSetting]:
        pass

    def create_multiple_scam_setting(self, user_id: str, list_create_data) -> NoReturn:
        existed_setting = self._list_scam_setting_orm(user_id)

        existed_dict = {s.category_id: s for s in existed_setting}
        creating_dict = {data.get("category_id"): data for data in list_create_data}
        list_create_orm = []
        for data in creating_dict.values():
            cat_id = data.get("category_id")
            if existed_dict.get(cat_id):
                updating_orm = existed_dict.get(cat_id)
                updating_orm.enabled = data.get("enabled", updating_orm.enabled)
                updating_orm.updated_at = now()
            else:
                list_create_orm.append(ScamSettingORM(
                    category_id=cat_id,
                    user_id=user_id,
                    enabled=data.get("enabled", True),
                    created_at=data.get("created_at", now())),
                )
        ScamSettingORM.objects.bulk_update(existed_setting, fields=["enabled", "updated_at"])
        ScamSettingORM.objects.bulk_create(list_create_orm, ignore_conflicts=False, batch_size=100)
        results = list(existed_setting) + list(list_create_orm)
        return [
            ModelParser.notification_parser().parse_user_scam_setting(s)
            for s in results
        ]

    def update_scam_setting(self, scam_setting_id: str, scam_update_data) -> Optional[ScamSetting]:
        pass
