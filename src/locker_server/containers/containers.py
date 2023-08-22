import os

from locker_server.settings import locker_server_settings


env = os.getenv("PROD_ENV", "dev")
if env != "dev":
    ServiceFactory = locker_server_settings.API_SERVICE_CLASS
else:
    from locker_server.containers.defaults.service import ServiceFactory


auth_service = ServiceFactory.auth_service()
user_service = ServiceFactory.user_service()

cipher_service = ServiceFactory.cipher_service()

team_member_service = ServiceFactory.team_member_service()

event_service = ServiceFactory.event_service()
