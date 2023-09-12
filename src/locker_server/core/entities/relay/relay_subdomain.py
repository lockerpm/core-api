from locker_server.core.entities.relay.relay_domain import RelayDomain
from locker_server.core.entities.user.user import User


class RelaySubdomain(object):
    def __init__(self, relay_subdomain_id: int, subdomain: str, created_time: float = None, is_deleted: bool = False,
                 user: User = None, domain: RelayDomain = None):
        self._relay_subdomain_id = relay_subdomain_id
        self._created_time = created_time
        self._is_deleted = is_deleted
        self._user = user
        self._domain = domain

    @property
    def relay_subdomain_id(self):
        return self._relay_subdomain_id

    @property
    def created_time(self):
        return self._created_time

    @property
    def is_deleted(self):
        return self._is_deleted

    @property
    def user(self):
        return self._user

    @property
    def domain(self):
        return self._domain


