from locker_server.api_orm.model_parsers.wrapper_specific_model_parser import get_specific_model_parser
from locker_server.api_orm.models import *
from locker_server.core.entities.payment.country import Country
from locker_server.core.entities.payment.customer import Customer
from locker_server.core.entities.payment.promo_code import PromoCode
from locker_server.core.entities.payment.promo_code_type import PromoCodeType
from locker_server.core.entities.payment.saas_market import SaasMarket
from locker_server.core.entities.user_plan.plan_type import PlanType
from locker_server.core.entities.user_plan.pm_plan import PMPlan
from locker_server.core.entities.user_plan.pm_user_plan import PMUserPlan


class PaymentParser:

    @classmethod
    def parse_country(cls, country_orm: CountryORM) -> Country:
        return Country(
            country_code=country_orm.country_code,
            country_name=country_orm.country_name,
            country_phone_code=country_orm.country_phone_code
        )

    @classmethod
    def parse_customer(cls, customer_orm: CustomerORM) -> Customer:
        return Customer(
            customer_id=customer_orm.id,
            full_name=customer_orm.full_name,
            organization=customer_orm.organization,
            address=customer_orm.address,
            city=customer_orm.city,
            state=customer_orm.state,
            postal_code=customer_orm.postal_code,
            phone_number=customer_orm.phone_number,
            last4=customer_orm.last4,
            brand=customer_orm.brand,
            country=cls.parse_country(country_orm=customer_orm.country) if customer_orm.country else None
        )

    @classmethod
    def parse_promo_code_type(cls, promo_code_type_orm: PromoCodeTypeORM) -> PromoCodeType:
        return PromoCodeType(
            name=promo_code_type_orm.name, description=promo_code_type_orm.description
        )

    @classmethod
    def parse_promo_code(cls, promo_code_orm: PromoCodeORM) -> PromoCode:
        user_parser = get_specific_model_parser("UserParser")
        return PromoCode(
            promo_code_id=promo_code_orm.id,
            created_time=promo_code_orm.created_time,
            expired_time=promo_code_orm.expired_time,
            remaining_times=promo_code_orm.remaining_times,
            valid=promo_code_orm.valid,
            value=promo_code_orm.value,
            code=promo_code_orm.code,
            limit_value=promo_code_orm.limit_value,
            duration=promo_code_orm.duration,
            specific_duration=promo_code_orm.specific_duration,
            currency=promo_code_orm.currency,
            description_en=promo_code_orm.description_en,
            description_vi=promo_code_orm.description_vi,
            promo_code_type=cls.parse_promo_code_type(promo_code_type_orm=promo_code_orm.type),
            is_saas_code=promo_code_orm.is_saas_code,
            saas_market=cls.parse_saas_market(saas_market_orm=promo_code_orm.saas_market),
            saas_plan=promo_code_orm.saas_plan,
            only_user=user_parser.parse_user(user_orm=promo_code_orm.only_user) if promo_code_orm.only_user else None,
            only_period=promo_code_orm.only_period,
        )

    @classmethod
    def parse_saas_market(cls, saas_market_orm: SaasMarketORM) -> SaasMarket:
        return SaasMarket(
            saas_market_id=saas_market_orm.id,
            name=saas_market_orm.name,
            lifetime_duration=saas_market_orm.lifetime_duration
        )
