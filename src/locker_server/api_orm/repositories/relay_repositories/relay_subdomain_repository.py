from typing import Optional, List

from django.db.models import Count, Sum
from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_relay_subdomain_model
from locker_server.core.entities.relay.relay_subdomain import RelaySubdomain
from locker_server.core.repositories.relay_repositories.relay_subdomain_repository import RelaySubdomainRepository

RelaySubdomainORM = get_relay_subdomain_model()
ModelParser = get_model_parser()


class RelaySubdomainORMRepository(RelaySubdomainRepository):
    # ------------------------ List RelaySubdomain resource ------------------- #
    def list_relay_subdomains(self, **filters) -> List[RelaySubdomain]:
        pass

    def list_user_relay_subdomains(self, user_id: int, **filters) -> List[RelaySubdomain]:
        relay_subdomains_orm = RelaySubdomainORM.objects.filter(user_id=user_id).annotate(
            num_alias=Count('relay_addresses'),
            num_spam=Sum('relay_addresses__num_spam'),
            num_forwarded=Sum('relay_addresses__num_forwarded'),
        ).order_by('created_time')
        is_deleted_param = filters.get("is_deleted")
        if is_deleted_param is not None:
            if is_deleted_param is False or is_deleted_param.lower() is "false":
                relay_subdomains_orm = relay_subdomains_orm.filter(is_deleted=False)
            elif is_deleted_param is True or is_deleted_param.lower() is "true":
                relay_subdomains_orm = relay_subdomains_orm.filter(is_deleted=True)

        return [ModelParser.relay_parser().parse_relay_subdomain(relay_domain_orm=relay_subdomain_orm)
                for relay_subdomain_orm in relay_subdomains_orm]

    def check_existed(self, **filters) -> bool:
        user_id_param = filters.get("user_id")
        if user_id_param:
            relay_subdomains_orm = RelaySubdomainORM.objects.filter(user_id=user_id_param)
        else:
            relay_subdomains_orm = RelaySubdomainORM.objects.all()
        is_deleted_param = filters.get("is_deleted")
        if is_deleted_param is not None:
            if is_deleted_param is False or is_deleted_param.lower() is "false":
                relay_subdomains_orm = relay_subdomains_orm.filter(is_deleted=False)
            elif is_deleted_param is True or is_deleted_param.lower() is "true":
                relay_subdomains_orm = relay_subdomains_orm.filter(is_deleted=True)
        return relay_subdomains_orm.exists()

    def check_used_subdomain(self, user_id: str, subdomain: str) -> bool:
        return RelaySubdomain.objects.exclude(user_id=user_id, is_deleted=False).filter(subdomain=subdomain).exists()

    # ------------------------ Get RelaySubdomain resource --------------------- #
    def get_relay_subdomain_by_id(self, relay_subdomain_id: str) -> Optional[RelaySubdomain]:
        try:
            relay_subdomain_orm = RelaySubdomainORM.objects.get(id=relay_subdomain_id).annotate(
                num_alias=Count('relay_addresses'),
                num_spam=Sum('relay_addresses__num_spam'),
                num_forwarded=Sum('relay_addresses__num_forwarded'),
            ).order_by('created_time')
        except RelaySubdomainORM.DoesNotExist:
            return None
        return ModelParser.relay_parser().parse_relay_subdomain(relay_subdomain_orm=relay_subdomain_orm)

    def get_relay_subdomain_by_subdomain(self, subdomain: str) -> Optional[RelaySubdomain]:
        try:
            relay_subdomain_orm = RelaySubdomainORM.objects.get(subdomain=subdomain)
        except RelaySubdomainORM.DoesNotExist:
            return None
        return ModelParser.relay_parser().parse_relay_subdomain(relay_subdomain_orm=relay_subdomain_orm)

    def get_first_subdomain_by_domain_id(self, user_id: str, domain_id: str) -> Optional[RelaySubdomain]:
        relay_subdomain_orm = RelaySubdomainORM.objects.filter(
            user_id=user_id,
            domain_id=domain_id,
            is_deleted=False
        ).first()
        return ModelParser.relay_parser().parse_relay_subdomain(relay_subdomain_orm=relay_subdomain_orm)

    # ------------------------ Create RelaySubdomain resource --------------------- #
    def create_relay_subdomain(self, relay_subdomain_create_data):
        new_relay_subdomain_orm = RelaySubdomainORM.create(**relay_subdomain_create_data)
        return ModelParser.relay_parser().parse_relay_subdomain(relay_subdomain_orm=new_relay_subdomain_orm)

    # ------------------------ Update RelaySubdomain resource --------------------- #

    def update_relay_subdomain(self, relay_subdomain_id: str, relay_subdomain_update_data):
        try:
            relay_subdomain_orm = RelaySubdomainORM.objects.get(id=relay_subdomain_id)
        except RelaySubdomainORM.DoesNotExist:
            return None
        relay_subdomain_orm.is_deleted = relay_subdomain_update_data.get("is_deleted", relay_subdomain_orm.is_deleted)
        relay_subdomain_orm.subdomain = relay_subdomain_update_data.get("subdomain", relay_subdomain_orm.subdomain)
        relay_subdomain_orm.save()
        return ModelParser.relay_parser().parse_relay_subdomain(relay_subdomain_orm=relay_subdomain_orm)

    # ------------------------ Delete RelaySubdomain resource --------------------- #
    def delete_relay_subdomain_by_id(self, relay_subdomain_id: str) -> bool:
        pass
