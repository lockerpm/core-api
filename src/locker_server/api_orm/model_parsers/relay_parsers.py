from locker_server.api_orm.model_parsers.wrapper_specific_model_parser import get_specific_model_parser
from src.locker_server.api_orm.models import *
from locker_server.core.entities.user.device import Device
from locker_server.core.entities.user.device_access_token import DeviceAccessToken
from locker_server.core.entities.user.exclude_domain import ExcludeDomain
from src.locker_server.core.entities.relay.relay_address import RelayAddress
from src.locker_server.core.entities.relay.relay_domain import RelayDomain
from src.locker_server.core.entities.relay.relay_subdomain import RelaySubdomain


class RelayParser:
    @classmethod
    def parse_relay_address(cls, relay_address_orm: RelayAddressORM) -> RelayAddress:
        user_parser = get_specific_model_parser("UserParser")
        user = user_parser.parse_user(user_orm=relay_address_orm.user)
        subdomain = cls.parse_relay_subdomain(relay_subdomain_orm=relay_address_orm.subdomain)
        domain = cls.parse_relay_domain(relay_domain_orm=relay_address_orm.domain)
        return RelayAddress(
            relay_address_id=relay_address_orm.id,
            user=user,
            address=relay_address_orm.address,
            subdomain=subdomain,
            domain=domain,
            enabled=relay_address_orm.enabled,
            block_spam=relay_address_orm.block_spam,
            description=relay_address_orm.description,
            created_time=relay_address_orm.created_time,
            updated_time=relay_address_orm.updated_time,
            num_forwarded=relay_address_orm.num_forwarded,
            num_blocked=relay_address_orm.num_blocked,
            num_replied=relay_address_orm.num_replied,
            num_spam=relay_address_orm.num_spam,
        )

    @classmethod
    def parse_relay_subdomain(cls, relay_subdomain_orm: RelaySubdomainORM) -> RelaySubdomain:
        user_parser = get_specific_model_parser("UserParser")
        user = user_parser.parse_user(user_orm=relay_subdomain_orm.user)
        domain = cls.parse_relay_domain(relay_domain_orm=relay_subdomain_orm.domain)
        return RelaySubdomain(
            relay_subdomain_id=relay_subdomain_orm.id,
            subdomain=relay_subdomain_orm.subdomain,
            created_time=relay_subdomain_orm.created_time,
            is_deleted=relay_subdomain_orm.is_deleted,
            user=user,
            domain=domain
        )

    @classmethod
    def parse_relay_domain(cls, relay_domain_orm: RelayDomainORM) -> RelayDomain:
        return RelayDomain(
            relay_domain_id=relay_domain_orm.id
        )
    @classmethod
    def parse_deleted_relay_address(cls,deleted_relay_address_orm:DeletedRelayAddressORM)->DeletedRelayAddress:
        return DeletedRelayAddress(

        )