from locker_server.api_orm.abstracts.enterprises.policy.policy import AbstractEnterprisePolicyORM


class EnterprisePolicyORM(AbstractEnterprisePolicyORM):
    class Meta(AbstractEnterprisePolicyORM.Meta):
        swappable = 'LS_ENTERPRISE_POLICY_MODEL'
        db_table = 'e_policy'
