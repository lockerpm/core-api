from typing import Optional

from locker_server.api_orm.models.wrapper import get_enterprise_avatar_model
from locker_server.core.repositories.enterprise_avatar_repository import EnterpriseAvatarRepository

EnterpriseAvatarORM = get_enterprise_avatar_model()


class EnterpriseAvatarORMRepository(EnterpriseAvatarRepository):
    # ------------------------ List EnterpriseAvatar resource ------------------- #

    # ------------------------ Get EnterpriseAvatar resource --------------------- #
    def get_enterprise_avatar_by_enterprise_id(self, enterprise_id: str) -> Optional[str]:
        enterprise_avatar_orm = EnterpriseAvatarORM.get(enterprise_id=enterprise_id)
        if enterprise_avatar_orm.avatar:
            return enterprise_avatar_orm.avatar.url
        return None

    # ------------------------ Create EnterpriseAvatar resource --------------------- #

    # ------------------------ Update EnterpriseAvatar resource --------------------- #
    def update_enterprise_avatar(self, enterprise_id: str, avatar) -> Optional[str]:
        enterprise_avatar_orm = EnterpriseAvatarORM.create(**{
            "enterprise_id": enterprise_id,
            "avatar": avatar,
        })
        if enterprise_avatar_orm.avatar:
            return enterprise_avatar_orm.avatar.url
        return None

        # ------------------------ Delete EnterpriseAvatar resource --------------------- #
