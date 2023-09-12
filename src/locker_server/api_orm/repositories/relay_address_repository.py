from typing import Optional, List

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_relay_address_model
from locker_server.core.entities.relay.relay_address import RelayAddress
from locker_server.core.repositories.relay_address_repository import RelayAddressRepository
from locker_server.shared.constants.token import *
from locker_server.shared.utils.app import now

RelayAddressORM = get_relay_address_model()
ModelParser = get_model_parser()


class RelayAddressORMRepository(RelayAddressRepository):
    # ------------------------ List RelayAddress resource ------------------- #
    def list_relay_addresses(self, **filters) -> List[RelayAddress]:
        relay_addresses_orm = RelayAddressORM.objects.all().order_by('created_time')
        return [ModelParser.relay_parser().parse_relay_address(relay_address_orm=relay_address_orm)
                for relay_address_orm in relay_addresses_orm]

    def list_user_relay_addresses(self, user_id: int, **filters) -> List[RelayAddress]:
        relay_addresses_orm = RelayAddressORM.objects.filter(
            user_id=user_id
        ).order_by('created_time')
        return [ModelParser.relay_parser().parse_relay_address(relay_address_orm=relay_address_orm)
                for relay_address_orm in relay_addresses_orm]

    def count_user_relay_addresses(self, user_id: int, **filters) -> int:
        user_relay_addresses_num = RelayAddressORM.objects.filter(user_id=user_id).count()
        return user_relay_addresses_num

    # ------------------------ Get RelayAddress resource --------------------- #

    def get_relay_address_by_id(self, relay_address_id: str) -> Optional[RelayAddress]:
        try:
            relay_address_orm = RelayAddressORM.objects.get(id=relay_address_id)
        except RelayAddressORM.DoesNotExist:
            return None
        return ModelParser.relay_parser().parse_relay_address(relay_address_orm=relay_address_orm)

    def get_oldest_user_relay_address(self, user_id: int) -> Optional[RelayAddress]:
        oldest_relay_address_orm = RelayAddressORM.objects.filter(user_id=user_id).order_by('created_time').first()
        if not oldest_relay_address_orm:
            return None
        return ModelParser.relay_parser().parse_relay_address(relay_address_orm=oldest_relay_address_orm)

    # ------------------------ Create RelayAddress resource --------------------- #
    def create_relay_address(self, relay_address_create_data):
        relay_address_orm = RelayAddressORM.create(**relay_address_create_data)
        return ModelParser.relay_parser.parse_relay_address(relay_address_orm=relay_address_orm)

    # ------------------------ Update RelayAddress resource --------------------- #
    def update_relay_address(self, relay_address_id: str, relay_address_update_data):
        try:
            relay_address_orm = RelayAddressORM.objects.get(id=relay_address_id)
        except RelayAddressORM.DoesNotExist:
            return None
        relay_address_orm.address = relay_address_update_data.get('address', relay_address_orm.address)
        relay_address_orm.enabled = relay_address_update_data.get('enabled', relay_address_orm.enabled)
        relay_address_orm.block_spam = relay_address_update_data.get('block_spam', relay_address_orm.block_spam)
        relay_address_orm.description = relay_address_update_data.get('description', relay_address_orm.description)
        relay_address_orm.updated_time = relay_address_update_data.get('updated_time', now())
        relay_address_orm.save()
        return ModelParser.relay_parser().parse_relay_address(relay_address_orm=relay_address_orm)

    # ------------------------ Delete RelayAddress resource --------------------- #
