from locker_server.api_orm.abstracts.enterprises.enterprises import AbstractEnterpriseORM


class EnterpriseORM(AbstractEnterpriseORM):
    class Meta(AbstractEnterpriseORM.Meta):
        swappable = 'LS_ENTERPRISE_MODEL'
        db_table = 'e_enterprises'

    @classmethod
    def create(cls, **data):
        pass
