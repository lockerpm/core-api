from hashlib import sha256
from typing import Tuple, Dict, List, Optional
from locker_server.core.repositories.relay_address_repository import RelayAddressRepository
from locker_server.core.repositories.user_repository import UserRepository

from locker_server.core.exceptions.relay_address_exception import *
from locker_server.core.exceptions.user_exception import UserDoesNotExistException
from locker_server.core.entities.relay.relay_address import RelayAddress


class RelayAddressService:
    """
    This class represents Use Cases related authentication
    """

    def __init__(self, relay_address_repository: RelayAddressRepository, user_repository: UserRepository):
        self.relay_address_repository = relay_address_repository
        self.user_repository = user_repository

    def list_user_relay_addresses(self, user_id: str, **filters):
        return self.relay_address_repository.list_user_relay_addresses(
            user_id=user_id,
            **filters
        )

    def get_relay_address_by_id(self, relay_address_id) -> Optional[RelayAddress]:
        relay_address = self.relay_address_repository.get_relay_address_by_id(relay_address_id=relay_address_id)
        if not relay_address:
            raise RelayAddressDoesNotExistException
        return relay_address

    def create_relay_address(self, user_id: int, relay_address_create_data):
        user = self.user_repository.get_user_by_id(user_id=user_id)
        if not user:
            raise UserDoesNotExistException
        allow_relay_premium = relay_address_create_data.get("allow_relay_premium", False)
        user_relay_addresses_num = self.relay_address_repository.count_user_addresses(user_id=user_id)
        if not allow_relay_premium and user_relay_addresses_num >= MAX_FREE_RElAY_DOMAIN:
            raise RelayAddressReachedException
        relay_address_create_data.update({
            'user_id': user_id
        })
        new_relay_address = self.relay_address_repository.create_relay_address()

    def update_relay_address(self, user_id: int, relay_address: RelayAddress, relay_address_update_data: dict) -> \
            Optional[
                RelayAddress]:
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
            # TODO: check valid address
            valid_address = self.check_valid_address(address=address, domain=relay_address.domain.relay_domain_id)
            if not valid_address:
                raise RelayAddressInvalidException
            relay_address.address = address
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

    def check_valid_address(self, address: str, domain: str):
        address_pattern_valid = self.valid_address_pattern(address)
        address_contains_bad_word = self.has_bad_words(address)
        address_is_blocklisted = self.is_blocklisted(address)
        address_is_locker_blocked = self.is_locker_blocked(address)
        address_already_deleted = self.deleted_relay_address_repository.check_exist_address_hash(
            address_hash=self.hash_address(address, domain)
        ).exists()
        if address_already_deleted is True or address_contains_bad_word or address_is_blocklisted or \
                not address_pattern_valid or address_is_locker_blocked:
            return False
        return True


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
