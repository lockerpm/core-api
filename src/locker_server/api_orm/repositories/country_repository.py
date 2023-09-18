from typing import Optional, List

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models import CountryORM
from locker_server.core.entities.payment.country import Country
from locker_server.core.repositories.country_repository import CountryRepository

ModelParser = get_model_parser()


class CountryORMRepository(CountryRepository):
    # ------------------------ List Country resource ------------------- #

    # ------------------------ Get Country resource --------------------- #
    def get_country_by_code(self, country_code: str) -> Optional[Country]:
        try:
            country_orm = CountryORM.objects.get(country_code=country_code)
        except CountryORM.DoesNotExist:
            return None
        return ModelParser.payment_parser().parse_country(country_orm=country_orm)

    def get_country_by_name(self, country_name: str) -> Optional[Country]:
        try:
            country_orm = CountryORM.objects.get(country_name=country_name)
        except CountryORM.DoesNotExist:
            return None
        return ModelParser.payment_parser().parse_country(country_orm=country_orm)
    # ------------------------ Create Country resource --------------------- #

    # ------------------------ Update Country resource --------------------- #

    # ------------------------ Delete Country resource --------------------- #
