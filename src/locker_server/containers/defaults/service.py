import dependency_injector.containers as containers
import dependency_injector.providers as providers

from locker_server.core.services import *
from locker_server.settings import locker_server_settings


RepositoryFactory = locker_server_settings.API_REPOSITORY_CLASS


class ServiceFactory(containers.DeclarativeContainer):
    """ IoC container of Services """

    auth_service = providers.Factory(
        AuthService,
        auth_repository=RepositoryFactory.auth_repository,
        device_access_token=RepositoryFactory.device_access_token_repository,
    )

    user_service = providers.Factory(
        UserService,
        user_repository=RepositoryFactory.user_repository,
        device_repository=RepositoryFactory.device_repository,
        device_access_token_repository=RepositoryFactory.device_access_token_repository,
        auth_repository=RepositoryFactory.auth_repository,
        user_plan_repository=RepositoryFactory.user_plan_repository,
        payment_repository=RepositoryFactory.payment_repository,
        plan_repository=RepositoryFactory.plan_repository,
        team_repository=RepositoryFactory.team_repository,
        team_member_repository=RepositoryFactory.team_member_repository,
        cipher_repository=RepositoryFactory.cipher_repository,
        enterprise_repository=RepositoryFactory.enterprise_repository,
        enterprise_member_repository=RepositoryFactory.enterprise_member_repository,
        enterprise_policy_repository=RepositoryFactory.enterprise_policy_repository,
        notification_setting_repository=RepositoryFactory.notification_setting_repository,
    )

    cipher_service = providers.Factory(
        CipherService,
        cipher_repository=RepositoryFactory.cipher_repository,
        team_repository=RepositoryFactory.team_repository,
        team_member_repository=RepositoryFactory.team_member_repository,
        user_plan_repository=RepositoryFactory.user_plan_repository,
    )

    team_member_service = providers.Factory(
        TeamMemberService,
        team_member_repository=RepositoryFactory.team_member_repository,

    )

    enterprise_group_service = providers.Factory(
        EnterpriseGroupService,

    )

    event_service = providers.Factory(
        EventService,
        event_repository=RepositoryFactory.event_repository,
    )
