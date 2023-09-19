from locker_server.api_orm.abstracts.enterprises.groups.group_members import AbstractEnterpriseGroupMemberORM


class EnterpriseGroupMemberORM(AbstractEnterpriseGroupMemberORM):
    class Meta(AbstractEnterpriseGroupMemberORM.Meta):
        swappable = 'LS_ENTERPRISE_GROUP_MEMBER_MODEL'
        db_table = 'e_groups_members'
