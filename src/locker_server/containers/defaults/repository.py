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

    exclude_domain_repository = providers.Factory(ExcludeDomainORMRepository)

    device_repository = providers.Factory(DeviceORMRepository)
    device_access_token_repository = providers.Factory(DeviceAccessTokenORMRepository)

    cipher_repository = providers.Factory(CipherORMRepository)

    team_repository = providers.Factory(TeamORMRepository)
    team_member_repository = providers.Factory(TeamMemberORMRepository)

    enterprise_repository = providers.Factory(EnterpriseORMRepository)
    enterprise_member_repository = providers.Factory(EnterpriseMemberORMRepository)
    enterprise_policy_repository = providers.Factory(EnterprisePolicyORMRepository)

    event_repository = providers.Factory(EventORMRepository)

    notification_category_repository = providers.Factory(NotificationCategoryORMRepository)
    notification_setting_repository = providers.Factory(NotificationSettingORMRepository)
