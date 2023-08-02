from locker_server.api_orm.abstracts.users.user_score import AbstractUserScoreORM


class UserScoreORM(AbstractUserScoreORM):
    class Meta(AbstractUserScoreORM.Meta):
        db_table = 'cs_user_score'
