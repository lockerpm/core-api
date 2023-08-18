from locker_server.api_orm.model_parsers.wrapper_specific_model_parser import get_specific_model_parser
from locker_server.api_orm.models import *
from locker_server.core.entities.enterprise.domain.domain import Domain
from locker_server.core.entities.enterprise.domain.domain_ownership import DomainOwnership
from locker_server.core.entities.enterprise.domain.ownership import Ownership
from locker_server.core.entities.enterprise.enterprise import Enterprise
from locker_server.core.entities.enterprise.member.enterprise_member import EnterpriseMember
from locker_server.core.entities.enterprise.member.enterprise_member_role import EnterpriseMemberRole


class EnterpriseParser:
    @classmethod
    def parse_enterprise(cls, enterprise_orm: EnterpriseORM) -> Enterprise:
        return Enterprise(
            enterprise_id=enterprise_orm.id,
            name=enterprise_orm.name,
            description=enterprise_orm.description,
            creation_date=enterprise_orm.creation_date,
            revision_date=enterprise_orm.revision_date,
            locked=enterprise_orm.locked,
            enterprise_name=enterprise_orm.enterprise_name,
            enterprise_address1=enterprise_orm.enterprise_address1,
            enterprise_address2=enterprise_orm.enterprise_address2,
            enterprise_phone=enterprise_orm.enterprise_phone,
            enterprise_country=enterprise_orm.enterprise_country,
            enterprise_postal_code=enterprise_orm.enterprise_postal_code,
            init_seats=enterprise_orm.init_seats,
            init_seats_expired_time=enterprise_orm.init_seats_expired_time,
        )

    @classmethod
    def parse_enterprise_member_role(cls, enterprise_member_role_orm: EnterpriseMemberRoleORM) -> EnterpriseMemberRole:
        return EnterpriseMemberRole(name=enterprise_member_role_orm.name)

    @classmethod
    def parse_ownership(cls, ownership_orm: OwnershipORM) -> Ownership:
        return Ownership(ownership_id=ownership_orm.id, description=ownership_orm.description)

    @classmethod
    def parse_domain(cls, domain_orm: DomainORM) -> Domain:
        return Domain(
            domain_id=domain_orm.id,
            created_time=domain_orm.created_time,
            updated_time=domain_orm.updated_time,
            domain=domain_orm.domain,
            root_domain=domain_orm.root_domain,
            verification=domain_orm.verification,
            auto_approve=domain_orm.auto_approve,
            is_notify_failed=domain_orm.is_notify_failed,
            enterprise=cls.parse_enterprise(enterprise_orm=domain_orm.enterprise)
        )

    @classmethod
    def parse_domain_ownership(cls, domain_ownership_orm: DomainOwnershipORM) -> DomainOwnership:
        return DomainOwnership(
            domain_ownership_id=domain_ownership_orm.id,
            key=domain_ownership_orm.key,
            value=domain_ownership_orm.value,
            verification=domain_ownership_orm.verification,
            domain=cls.parse_domain(domain_orm=domain_ownership_orm.domain),
            ownership=cls.parse_ownership(ownership_orm=domain_ownership_orm.ownership)
        )

    @classmethod
    def parse_enterprise_member(cls, enterprise_member_orm: EnterpriseMemberORM) -> EnterpriseMember:
        user = get_specific_model_parser("UserParser").parse_user(user_orm=enterprise_member_orm.user) \
            if enterprise_member_orm.user else None
        domain = cls.parse_domain(domain_orm=enterprise_member_orm.domain) if enterprise_member_orm.domain else None
        return EnterpriseMember(
            enterprise_member_id=enterprise_member_orm.id,
            access_time=enterprise_member_orm.access_time,
            is_default=enterprise_member_orm.is_default,
            is_activated=enterprise_member_orm.is_activated,
            status=enterprise_member_orm.status,
            email=enterprise_member_orm.email,
            token_invitation=enterprise_member_orm.token_invitation,
            user=user,
            enterprise=cls.parse_enterprise(enterprise_orm=enterprise_member_orm.enterprise),
            role=cls.parse_enterprise_member_role(enterprise_member_role_orm=enterprise_member_orm.role),
            domain=domain
        )
