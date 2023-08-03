from locker_server.api_orm.abstracts.relay.relay_addresses import AbstractRelayAddressORM


class RelayAddressORM(AbstractRelayAddressORM):
    class Meta(AbstractRelayAddressORM.Meta):
        swappable = 'LS_RELAY_ADDRESS_MODEL'
        db_table = 'cs_relay_addresses'

    @classmethod
    def create_atomic(cls, user_id, **data):
        pass

    @classmethod
    def create(cls, user, **data):
        pass
