from locker_server.api_orm.abstracts.enterprises.groups.groups import AbstractEnterpriseGroupORM


class EnterpriseGroupORM(AbstractEnterpriseGroupORM):
    class Meta(AbstractEnterpriseGroupORM.Meta):
        swappable = 'LS_ENTERPRISE_GROUP_MODEL'
        db_table = 'e_enterprise_groups'

