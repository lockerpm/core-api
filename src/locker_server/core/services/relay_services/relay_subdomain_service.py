import re
from typing import Optional

from locker_server.core.repositories.relay_repositories.relay_address_repository import RelayAddressRepository
from src.locker_server.core.repositories.relay_repositories.relay_subdomain_repository import RelaySubdomainRepository

from locker_server.core.exceptions.relay_exceptions.relay_subdomain_exception import *
from locker_server.core.exceptions.user_exception import UserDoesNotExistException
from locker_server.core.repositories.user_repository import UserRepository
from locker_server.core.entities.relay.relay_subdomain import RelaySubdomain
from locker_server.shared.constants.relay_blacklist import RELAY_BAD_WORDS, RELAY_BLOCKLISTED, \
    RELAY_LOCKER_BLOCKED_CHARACTER


class RelaySubdomainService:
    """
    This class represents Use Cases related relay subdomain
    """

    def __init__(self, relay_subdomain_repository: RelaySubdomainRepository, user_repository: UserRepository,
                 relay_address_repository: RelayAddressRepository):
        self.user_repository = user_repository
        self.relay_subdomain_repository = relay_subdomain_repository
        self.relay_address_repository = relay_address_repository

    def list_user_relay_subdomain(self, user_id: int, **filters):
        return self.relay_subdomain_repository.list_user_relay_subdomains(
            user_id=user_id,
            **filters
        )

    def check_allow_created(self, user_id: int) -> bool:
        return self.relay_subdomain_repository.check_existed(**{
            "user_id": user_id,
            "is_deleted": False
        })

    def create_relay_subdomain(self, user_id: int, relay_subdomain_create_data) -> RelaySubdomain:
        user = self.user_repository.get_user_by_id(user_id=user_id)
        if not user:
            raise UserDoesNotExistException
        is_allowed = self.check_allow_created(user_id=user_id)
        if not is_allowed:
            raise MaxRelaySubdomainReachedException
        subdomain = relay_subdomain_create_data.get("subdomain")
        is_valid_subdomain = self.valid_subdomain(subdomain=subdomain)
        if not is_valid_subdomain:
            raise RelaySubdomainInvalidException
        existed_relay_subdomain = self.relay_subdomain_repository.get_relay_subdomain_by_subdomain(subdomain=subdomain)
        if existed_relay_subdomain:
            raise RelaySubdomainExistedException
        relay_subdomain_create_data.update({
            "user_id": user_id
        })
        new_relay_subdomain = self.relay_subdomain_repository.create_relay_subdomain(
            relay_subdomain_create_data=relay_subdomain_create_data)
        return new_relay_subdomain

    def update_relay_subdomain(self, user_id: str, relay_subdomain_id: str, relay_subdomain_update_data) -> Optional[
        RelaySubdomain]:
        new_subdomain = relay_subdomain_update_data.get("subdomain")
        is_valid_subdomain = self.valid_subdomain(subdomain=new_subdomain)
        if not is_valid_subdomain:
            raise RelaySubdomainInvalidException
        is_used_subdomain = self.relay_subdomain_repository.check_used_subdomain(
            user_id=user_id,
            subdomain=new_subdomain
        )
        if is_used_subdomain:
            raise RelaySubdomainAlreadyUsedException
        updated_relay_subdomain = self.relay_subdomain_repository.update_relay_subdomain(
            relay_subdomain_id=relay_subdomain_id,
            relay_subdomain_update_data=relay_subdomain_update_data
        )
        if not updated_relay_subdomain:
            raise RelaySubdomainDoesNotExistException
        return updated_relay_subdomain

    def get_first_subdomain_by_domain_id(self, user_id: str, domain_id: str) -> RelaySubdomain:
        return self.relay_subdomain_repository.get_first_subdomain_by_domain_id(
            user_id=user_id,
            domain_id=domain_id
        )

    def get_relay_subdomain_by_id(self, relay_subdomain_id) -> Optional[RelaySubdomain]:
        relay_subdomain = self.relay_subdomain_repository.get_relay_subdomain_by_id(
            relay_subdomain_id=relay_subdomain_id
        )
        if not relay_subdomain:
            raise RelaySubdomainDoesNotExistException
        return relay_subdomain

    def soft_delete_relay_subdomain(self, relay_subdomain: RelaySubdomain) -> bool:
        relay_subdomain_update_data = {
            "is_deleted": True
        }
        soft_deleted_subdomain = self.relay_subdomain_repository.update_relay_subdomain(
            relay_subdomain_id=relay_subdomain.relay_subdomain_id,
            relay_subdomain_update_data=relay_subdomain_update_data
        )
        if not soft_deleted_subdomain:
            raise RelaySubdomainDoesNotExistException
        return soft_deleted_subdomain

    @classmethod
    def valid_subdomain(cls, subdomain) -> bool:
        address_pattern_valid = cls.valid_subdomain_pattern(subdomain)
        address_contains_bad_word = cls.has_bad_words(subdomain)
        address_is_blocklisted = cls.is_blocklisted(subdomain)
        address_is_locker_blocked = cls.is_locker_blocked(subdomain)

        if address_contains_bad_word or address_is_blocklisted or not address_pattern_valid or \
                address_is_locker_blocked:
            return False
        return True

    @classmethod
    def valid_subdomain_pattern(cls, address):
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
