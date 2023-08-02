from locker_server.api_orm.abstracts.relay.relay_subdomains import AbstractRelaySubdomainORM
from locker_server.shared.constants.relay_address import DEFAULT_RELAY_DOMAIN


class RelaySubdomainORM(AbstractRelaySubdomainORM):
    class Meta(AbstractRelaySubdomainORM.Meta):
        swappable = 'LS_RELAY_SUBDOMAIN_MODEL'
        db_table = 'cs_relay_subdomains'

    @classmethod
    def create_atomic(cls, user_id, subdomain: str, domain_id: str = DEFAULT_RELAY_DOMAIN, is_deleted=False):
        pass

