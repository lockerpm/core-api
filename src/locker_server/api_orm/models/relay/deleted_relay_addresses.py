from locker_server.api_orm.abstracts.relay.deleted_relay_addresses import AbstractDeletedRelayAddressORM


class DeletedRelayAddressORM(AbstractDeletedRelayAddressORM):
    class Meta(AbstractDeletedRelayAddressORM.Meta):
        swappable = 'LS_RELAY_DELETED_ADDRESS_MODEL'
        db_table = 'cs_deleted_relay_addresses'

    @classmethod
    def create(cls, **kwargs):
        pass
