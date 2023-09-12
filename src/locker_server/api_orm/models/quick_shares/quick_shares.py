from locker_server.api_orm.abstracts.quick_shares.quick_shares import AbstractQuickShareORM


class QuickShareORM(AbstractQuickShareORM):
    class Meta(AbstractQuickShareORM.Meta):
        swappable = 'LS_QUICK_SHARE_MODEL'
        db_table = 'cs_quick_shares'

    @classmethod
    def create(cls, **data):
        pass
