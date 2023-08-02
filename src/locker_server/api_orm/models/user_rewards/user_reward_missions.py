from locker_server.api_orm.abstracts.user_rewards.user_reward_missions import AbstractUserRewardMissionORM


class UserRewardMissionORM(AbstractUserRewardMissionORM):
    class Meta(AbstractUserRewardMissionORM.Meta):
        db_table = 'cs_user_reward_missions'

