import dependency_injector.containers as containers
import dependency_injector.providers as providers

from locker_server.api_orm.repositories import *


class RepositoryFactory(containers.DeclarativeContainer):
    """ IoC container of Repositories """

    auth_repository = providers.Factory(AuthORMRepository)
    user_repository = providers.Factory(UserORMRepository)
    plan_repository = providers.Factory(PlanORMRepository)
    user_plan_repository = providers.Factory(UserPlanORMRepository)
    payment_repository = providers.Factory(PaymentORMRepository)

    device_access_token_repository = providers.Factory(DeviceAccessTokenORMRepository)

    team_member_repository = providers.Factory(TeamMemberORMRepository)

    enterprise_member_repository = providers.Factory(EnterpriseMemberORMRepository)
