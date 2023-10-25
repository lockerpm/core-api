import os

from locker_server.api_orm.abstracts.enterprises.enterprise_avatars import AbstractEnterpriseAvatarORM


class EnterpriseAvatarORM(AbstractEnterpriseAvatarORM):
    class Meta(AbstractEnterpriseAvatarORM.Meta):
        swappable = 'LS_ENTERPRISE_AVATAR_MODEL'
        db_table = 'e_enterprise_avatars'

    @classmethod
    def create(cls, **data):
        enterprise_id = data.get("enterprise_id")
        avatar = data.get("avatar")
        enterprise_avatar_orm, is_created = cls.objects.get_or_create(
            enterprise_id=enterprise_id,
            defaults={
                "enterprise_id": enterprise_id,
                "avatar": avatar
            }
        )
        if not is_created:
            if enterprise_avatar_orm.avatar:
                old_avatar = enterprise_avatar_orm.avatar
                try:
                    os.remove(old_avatar.path)
                except FileNotFoundError:
                    pass
            enterprise_avatar_orm.avatar = avatar
            enterprise_avatar_orm.save()

        return enterprise_avatar_orm

    @classmethod
    def get(cls, enterprise_id: str):
        enterprise_avatar_orm, is_created = cls.objects.get_or_create(
            enterprise_id=enterprise_id,
            defaults={
                "enterprise_id": enterprise_id
            }
        )
        return enterprise_avatar_orm
