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
    country_repository = providers.Factory(CountryORMRepository)

    exclude_domain_repository = providers.Factory(ExcludeDomainORMRepository)

    device_repository = providers.Factory(DeviceORMRepository)
    device_access_token_repository = providers.Factory(DeviceAccessTokenORMRepository)

    cipher_repository = providers.Factory(CipherORMRepository)
    folder_repository = providers.Factory(FolderORMRepository)

    team_repository = providers.Factory(TeamORMRepository)
    team_member_repository = providers.Factory(TeamMemberORMRepository)
    collection_repository = providers.Factory(CollectionORMRepository)
    sharing_repository = providers.Factory(SharingORMRepository)

    enterprise_repository = providers.Factory(EnterpriseORMRepository)
    enterprise_member_repository = providers.Factory(EnterpriseMemberORMRepository)
    enterprise_policy_repository = providers.Factory(EnterprisePolicyORMRepository)

    event_repository = providers.Factory(EventORMRepository)

    notification_category_repository = providers.Factory(NotificationCategoryORMRepository)
    notification_setting_repository = providers.Factory(NotificationSettingORMRepository)

    relay_address_repository = providers.Factory(RelayAddressORMRepository)
    deleted_relay_address_repository = providers.Factory(DeletedRelayAddressORMRepository)
    relay_subdomain_repository = providers.Factory(RelaySubdomainORMRepository)
    reply_repository = providers.Factory(ReplyORMRepository)

    affiliate_submission_repository = providers.Factory(AffiliateSubmissionORMRepository)

    release_repository = providers.Factory(ReleaseORMRepository)
