import os

from locker_server.settings import locker_server_settings

env = os.getenv("PROD_ENV", "dev")
if env != "dev":
    ServiceFactory = locker_server_settings.API_SERVICE_CLASS
else:
    from locker_server.containers.defaults.service import ServiceFactory

resource_service = ServiceFactory.resource_service()

auth_service = ServiceFactory.auth_service()
user_service = ServiceFactory.user_service()
family_service = ServiceFactory.family_service()

exclude_domain_service = ServiceFactory.exclude_domain_service()

cipher_service = ServiceFactory.cipher_service()
folder_service = ServiceFactory.folder_service()

team_member_service = ServiceFactory.team_member_service()
collection_service = ServiceFactory.collection_service()
sharing_service = ServiceFactory.sharing_service()

enterprise_service = ServiceFactory.enterprise_service()

event_service = ServiceFactory.event_service()
relay_address_service = ServiceFactory.relay_address_service()
relay_subdomain_service = ServiceFactory.relay_subdomain_service()
reply_service = ServiceFactory.reply_service()

affiliate_submission_service = ServiceFactory.affiliate_submission_service()

release_service = ServiceFactory.release_service()
