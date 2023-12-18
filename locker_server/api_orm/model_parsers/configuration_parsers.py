from locker_server.api_orm.models import *
from locker_server.core.entities.configuration.app_info import AppInfo
from locker_server.core.entities.configuration.mail_configuration import MailConfiguration
from locker_server.core.entities.configuration.mail_provider import MailProvider


class ConfigurationParser:
    @classmethod
    def parse_mail_provider(cls, mail_provider_orm: MailProviderORM) -> MailProvider:
        return MailProvider(
            mail_provider_id=mail_provider_orm.id, name=mail_provider_orm.name, available=mail_provider_orm.available
        )

    @classmethod
    def parse_mail_configuration(cls, mail_configuration_orm: MailConfigurationORM) -> MailConfiguration:
        return MailConfiguration(
            mail_provider=cls.parse_mail_provider(mail_provider_orm=mail_configuration_orm.mail_provider),
            mail_provider_options=mail_configuration_orm.get_mail_provider_option(),
            sending_domain=mail_configuration_orm.sending_domain,
            from_email=mail_configuration_orm.from_email,
            from_name=mail_configuration_orm.from_name,
        )

    @classmethod
    def parse_app_info(cls, app_info_orm: AppInfoORM) -> AppInfo:
        try:
            avatar_file = app_info_orm.logo
            logo_url = avatar_file.url
        except:
            logo_url = None
        return AppInfo(
            logo=logo_url,
            name=app_info_orm.name,
            creation_date=app_info_orm.creation_date,
            revision_date=app_info_orm.revision_date
        )
