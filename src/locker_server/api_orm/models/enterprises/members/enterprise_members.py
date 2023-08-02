from locker_server.api_orm.abstracts.enterprises.members.enterprise_members import AbstractEnterpriseMemberORM


class EnterpriseMemberORM(AbstractEnterpriseMemberORM):
    class Meta(AbstractEnterpriseMemberORM.Meta):
        swappable = 'LS_ENTERPRISE_MEMBER_MODEL'
        db_table = 'e_members'
        unique_together = ('user', 'enterprise', 'role')