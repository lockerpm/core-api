import os
from typing import Optional, Dict

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models import AppInfoORM
from locker_server.core.entities.configuration.app_info import AppInfo
from locker_server.core.repositories.app_info_repository import AppInfoRepository
from locker_server.shared.utils.app import now

ModelParser = get_model_parser()


class AppInfoORMRepository(AppInfoRepository):
    # ------------------------ List AppInfo resource ------------------- #

    # ------------------------ Get AppInfo resource --------------------- #
    def get_app_info(self) -> Optional[AppInfo]:
        try:
            app_info_orm = AppInfoORM.objects.get()
            return ModelParser.configuration_parser().parse_app_info(
                app_info_orm=app_info_orm
            )
        except AppInfoORM.DoesNotExist:
            return None

    def get_app_logo(self) -> Optional[str]:
        try:
            app_info_orm = AppInfoORM.objects.get()
        except AppInfoORM.DoesNotExist:
            app_info_orm = AppInfoORM.create(**{
                "name": "My app"
            })
        try:
            return app_info_orm.logo.url
        except (FileNotFoundError, ValueError):
            return None

    # ------------------------ Create MailConfiguration resource --------------------- #

    # ------------------------ Update MailConfiguration resource --------------------- #
    def update_logo(self, new_logo) -> str:
        try:
            app_info_orm = AppInfoORM.objects.get()
        except AppInfoORM.DoesNotExist:
            app_info_orm = AppInfoORM.create(**{
                "name": "My app"
            })
        try:
            old_logo = app_info_orm.logo
            os.remove(old_logo.path)
        except (FileNotFoundError, ValueError):
            pass
        app_info_orm.logo = new_logo
        app_info_orm.save()
        return app_info_orm.logo.url

    def update_app_info(self, update_data: Dict) -> AppInfo:
        is_created = False
        try:
            app_info_orm = AppInfoORM.objects.get()
        except AppInfoORM.DoesNotExist:
            app_info_orm = AppInfoORM.create(**update_data)
            is_created = True
        app_info_orm.name = update_data.get("name", app_info_orm.name)
        if not is_created:
            app_info_orm.revision_date = now()
        app_info_orm.save()
        return ModelParser.configuration_parser().parse_app_info(
            app_info_orm=app_info_orm
        )

    # ------------------------ Delete MailConfiguration resource --------------------- #
