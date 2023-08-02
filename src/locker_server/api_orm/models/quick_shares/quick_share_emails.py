from locker_server.api_orm.abstracts.quick_shares.quick_share_emails import AbstractQuickShareEmailORM


class QuickShareEmailORM(AbstractQuickShareEmailORM):
    class Meta:
        swappable = 'LS_QUICK_SHARE_EMAIL_MODEL'
        db_table = 'cs_quick_share_emails'
