from locker_server.api_orm.abstracts.enterprises.domains.domains import AbstractDomainORM


class DomainORM(AbstractDomainORM):

    class Meta(AbstractDomainORM.Meta):
        swappable = 'LS_ENTERPRISE_DOMAIN_MODEL'
        db_table = 'e_domains'

    @classmethod
    def create(cls, enterprise, domain: str, root_domain: str, verification: bool = False):
        pass