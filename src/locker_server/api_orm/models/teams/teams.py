from locker_server.api_orm.abstracts.teams.teams import AbstractTeamORM


class TeamORM(AbstractTeamORM):
    class Meta:
        swappable = 'LS_TEAM_MODEL'
        db_table = 'cs_teams'

    @classmethod
    def create(cls, **data):
        pass
