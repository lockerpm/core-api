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
        device_access_token_repository=RepositoryFactory.device_access_token_repository,
    )

    resource_service = providers.Factory(
        ResourceService,
        plan_repository=RepositoryFactory.plan_repository,
        country_repository=RepositoryFactory.country_repository
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
    family_service = providers.Factory(
        FamilyService,
        user_repository=RepositoryFactory.user_repository,
        user_plan_repository=RepositoryFactory.user_plan_repository,
    )

    exclude_domain_service = providers.Factory(
        ExcludeDomainService,
        exclude_domain_repository=RepositoryFactory.exclude_domain_repository
    )

    cipher_service = providers.Factory(
        CipherService,
        cipher_repository=RepositoryFactory.cipher_repository,
        folder_repository=RepositoryFactory.folder_repository,
        team_repository=RepositoryFactory.team_repository,
        team_member_repository=RepositoryFactory.team_member_repository,
        user_plan_repository=RepositoryFactory.user_plan_repository,
    )
    folder_service = providers.Factory(
        FolderService,
        folder_repository=RepositoryFactory.folder_repository,
        cipher_repository=RepositoryFactory.cipher_repository,
    )

    team_member_service = providers.Factory(
        TeamMemberService,
        team_member_repository=RepositoryFactory.team_member_repository,

    )
    collection_service = providers.Factory(
        CollectionService,
        collection_repository=RepositoryFactory.collection_repository
    )
    sharing_service = providers.Factory(
        SharingService,
        sharing_repository=RepositoryFactory.sharing_repository,
        team_repository=RepositoryFactory.team_repository,
        team_member_repository=RepositoryFactory.team_member_repository,
    )

    enterprise_service = providers.Factory(
        EnterpriseService,
        enterprise_repository=RepositoryFactory.enterprise_repository,
        enterprise_member_repository=RepositoryFactory.enterprise_member_repository,
        enterprise_policy_repository=RepositoryFactory.enterprise_policy_repository
    )
    enterprise_group_service = providers.Factory(
        EnterpriseGroupService,

    )

    event_service = providers.Factory(
        EventService,
        event_repository=RepositoryFactory.event_repository,
    )

    relay_address_service = providers.Factory(
        RelayAddressService,
        relay_address_repository=RepositoryFactory.relay_address_repository,
        user_repository=RepositoryFactory.user_repository,
        deleted_relay_address_repository=RepositoryFactory.deleted_relay_address_repository
    )
    relay_subdomain_service = providers.Factory(
        RelaySubdomainService,
        relay_subdomain_repository=RepositoryFactory.relay_subdomain_repository,
        user_repository=RepositoryFactory.user_repository,
        relay_address_repository=RepositoryFactory.relay_address_repository,
        deleted_relay_address_repository=RepositoryFactory.deleted_relay_address_repository
    )
    reply_service = providers.Factory(
        ReplyService,
        reply_repository=RepositoryFactory.reply_repository
    )

    affiliate_submission_service = providers.Factory(
        AffiliateSubmissionService,
        affiliate_submission_repository=RepositoryFactory.affiliate_submission_repository,
        country_repository=RepositoryFactory.country_repository
    )
    release_service = providers.Factory(
        ReleaseService,
        release_repository=RepositoryFactory.release_repository
    )
    notification_setting_service = providers.Factory(
        NotificationSettingService,
        notification_setting_repository=RepositoryFactory.notification_setting_repository,
        user_repository=RepositoryFactory.user_repository
    )
