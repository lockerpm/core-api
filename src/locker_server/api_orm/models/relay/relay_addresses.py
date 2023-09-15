from locker_server.api_orm.abstracts.relay.relay_addresses import AbstractRelayAddressORM

from locker_server.shared.utils.app import random_n_digit

from locker_server.shared.utils.app import now


class RelayAddressORM(AbstractRelayAddressORM):
    class Meta(AbstractRelayAddressORM.Meta):
        swappable = 'LS_RELAY_ADDRESS_MODEL'
        db_table = 'cs_relay_addresses'

    @classmethod
    def create_atomic(cls, user_id, **data):
        pass

    @classmethod
    def create(cls, **data):
        user_id = data.get('user_id')
        domain_id = data.get("domain_id") or DEFAULT_RELAY_DOMAIN
        description = data.get("description", "")
        subdomain_id = data.get("subdomain_id")
        while True:
            address = random_n_digit(n=6)
            if cls.objects.filter(address=address).exists() is True:
                continue
            if cls.valid_address(address=address, domain=domain_id) is False:
                continue
            break
        new_relay_address = cls(
            user_id=user_id, address=address, domain_id=domain_id, subdomain_id=subdomain_id,
            created_time=now(), description=description,
        )
        new_relay_address.save()

        return new_relay_address
