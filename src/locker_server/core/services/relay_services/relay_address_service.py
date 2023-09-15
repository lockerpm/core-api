import re
from hashlib import sha256
from typing import Optional, NoReturn
from locker_server.core.repositories.relay_repositories.relay_address_repository import RelayAddressRepository
from locker_server.core.repositories.user_repository import UserRepository
from locker_server.core.repositories.relay_repositories.deleted_relay_address_repository import \
    DeletedRelayAddressRepository

from locker_server.core.exceptions.relay_exceptions.relay_address_exception import *
from locker_server.core.exceptions.user_exception import UserDoesNotExistException
from locker_server.core.entities.relay.relay_address import RelayAddress
from locker_server.shared.constants.relay_address import MAX_FREE_RElAY_DOMAIN
from locker_server.shared.constants.relay_blacklist import RELAY_BAD_WORDS, RELAY_BLOCKLISTED, \
    RELAY_LOCKER_BLOCKED_CHARACTER


class RelayAddressService:
    """
    This class represents Use Cases related relay address
    """

    def __init__(self, relay_address_repository: RelayAddressRepository, user_repository: UserRepository,
                 deleted_relay_address_repository: DeletedRelayAddressRepository):
        self.relay_address_repository = relay_address_repository
        self.user_repository = user_repository
        self.deleted_relay_address_repository = deleted_relay_address_repository

    def list_user_relay_addresses(self, user_id: int, **filters):
        return self.relay_address_repository.list_user_relay_addresses(
            user_id=user_id,
            **filters
        )

    def get_relay_address_by_id(self, relay_address_id) -> Optional[RelayAddress]:
        relay_address = self.relay_address_repository.get_relay_address_by_id(relay_address_id=relay_address_id)
        if not relay_address:
            raise RelayAddressDoesNotExistException
        return relay_address

    def create_relay_address(self, user_id: int, relay_address_create_data) -> Optional[RelayAddress]:
        user = self.user_repository.get_user_by_id(user_id=user_id)
        if not user:
            raise UserDoesNotExistException
        relay_address_create_data.update({
            'user_id': user_id
        })
        new_relay_address = self.relay_address_repository.create_relay_address(relay_address_create_data)
        if not new_relay_address:
            raise RelayAddressReachedException
        return new_relay_address

    def update_relay_address(self, user_id: int, relay_address: RelayAddress,
                             relay_address_update_data: dict) -> Optional[RelayAddress]:
        address = relay_address_update_data.get("address") or relay_address.address

        if address != relay_address.address:
            # Only allow update the first address
            oldest_relay_address = self.relay_address_repository.get_oldest_user_relay_address(
                user_id=user_id,
            )
            if not oldest_relay_address or oldest_relay_address.relay_address_id != relay_address.relay_address_id:
                raise RelayAddressUpdateDeniedException
            existed_address = self.relay_address_repository.get_relay_address_by_address(address=address)
            if existed_address:
                raise RelayAddressExistedException
            full_domain = self.get_full_domain(relay_address=relay_address)
            valid_address = self.check_valid_address(address=address, domain=full_domain)
            if not valid_address:
                raise RelayAddressInvalidException

        relay_address_update_data.update({
            'address': address
        })
        allow_relay_premium = relay_address_update_data.get("allow_relay_premium")
        if not allow_relay_premium:
            relay_address_update_data.update({
                'enabled': relay_address.enabled,
                'block_spam': relay_address.block_spam
            })
        relay_address = self.relay_address_repository.update_relay_address(
            relay_address_id=relay_address.relay_address_id,
            relay_address_update_data=relay_address_update_data
        )
        if not relay_address:
            raise RelayAddressDoesNotExistException
        return relay_address

    def delete_relay_address(self, relay_address: RelayAddress) -> bool:
        deleted_relay_address = self.relay_address_repository.delete_relay_address_by_id(
            relay_address_id=relay_address.relay_address_id
        )
        if not deleted_relay_address:
            raise RelayAddressDoesNotExistException
        full_domain = self.get_full_domain(relay_address=relay_address)
        self.deleted_relay_address_repository.create_deleted_relay_address(
            deleted_relay_address_create_data={
                "address_hash": self.hash_address(address=relay_address.address, domain=full_domain),
                "num_forwarded": relay_address.num_forwarded,
                "num_blocked": relay_address.num_blocked,
                "num_replied": relay_address.num_replied,
                "num_spam": relay_address.num_spam,
            })
        return relay_address.relay_address_id

    def delete_relay_addresses_by_subdomain_id(self, subdomain_id: str) -> NoReturn:
        relay_addresses = self.relay_address_repository.list_relay_addresses(**{
            "subdomain_id": subdomain_id
        })
        for relay_address in relay_addresses:
            self.delete_relay_address(relay_address=relay_address)

    def update_block_spam(self, relay_address: RelayAddress) -> Optional[RelayAddress]:
        relay_address_update_data = {
            'block_spam': not relay_address.block_spam
        }
        updated_relay_address = self.relay_address_repository.update_relay_address(
            relay_address_id=relay_address.relay_address_id,
            relay_address_update_data=relay_address_update_data
        )
        if not updated_relay_address:
            raise RelayAddressDoesNotExistException
        return updated_relay_address

    def update_enabled(self, relay_address: RelayAddress) -> Optional[RelayAddress]:
        relay_address_update_data = {
            'enabled': not relay_address.enabled
        }
        updated_relay_address = self.relay_address_repository.update_relay_address(
            relay_address_id=relay_address.relay_address_id,
            relay_address_update_data=relay_address_update_data
        )
        if not updated_relay_address:
            raise RelayAddressDoesNotExistException
        return updated_relay_address

    def get_relay_address_by_full_domain(self, address: str, domain_id: str, subdomain: str = None) -> Optional[
        RelayAddress]:
        relay_address = self.relay_address_repository.get_relay_address_by_full_domain(
            address=address,
            domain_id=domain_id,
            subdomain=subdomain
        )
        return relay_address

    def check_valid_address(self, address: str, domain: str):
        address_pattern_valid = self.valid_address_pattern(address)
        address_contains_bad_word = self.has_bad_words(address)
        address_is_blocklisted = self.is_blocklisted(address)
        address_is_locker_blocked = self.is_locker_blocked(address)
        address_already_deleted = self.deleted_relay_address_repository.check_exist_address_hash(
            address_hash=self.hash_address(address, domain)
        )
        if address_already_deleted is True or address_contains_bad_word or address_is_blocklisted or \
                not address_pattern_valid or address_is_locker_blocked:
            return False
        return True

    @classmethod
    def get_full_domain(cls, relay_address: RelayAddress):
        if relay_address.subdomain:
            return f"{relay_address.subdomain.subdomain}.{relay_address.domain.relay_domain_id}"
        else:
            return relay_address.domain.relay_domain_id

    @classmethod
    def valid_address_pattern(cls, address):
        # The address can't start or end with a hyphen, must be 1 - 63 lowercase alphanumeric characters
        valid_address_pattern = re.compile("^(?!-)[a-z0-9-]{1,63}(?<!-)$")
        return valid_address_pattern.match(address) is not None

    @classmethod
    def has_bad_words(cls, value):
        for bad_word in RELAY_BAD_WORDS:
            bad_word = bad_word.strip()
            if len(bad_word) <= 4 and bad_word == value:
                return True
            if len(bad_word) > 4 and bad_word in value:
                return True
        return False

    @classmethod
    def is_blocklisted(cls, value):
        return any(blocked_word == value for blocked_word in RELAY_BLOCKLISTED)

    @classmethod
    def is_locker_blocked(cls, value):
        for blocked_word in RELAY_LOCKER_BLOCKED_CHARACTER:
            if blocked_word in value:
                return True
        return False

    @classmethod
    def hash_address(cls, address, domain):
        return sha256(f"{address}@{domain}".encode("utf-8")).hexdigest()
