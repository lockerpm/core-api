from locker_server.api_orm.abstracts.members.team_members import AbstractTeamMemberORM


class TeamMemberORM(AbstractTeamMemberORM):
    class Meta:
        swappable = 'LS_TEAM_MEMBER_MODEL'
        db_table = 'cs_team_members'
