from typing import List, Dict

from locker_server.core.entities.configuration.mail_provider import MailProvider
from locker_server.core.entities.payment.country import Country
from locker_server.core.entities.user_plan.pm_plan import PMPlan
from locker_server.core.repositories.country_repository import CountryRepository
from locker_server.core.repositories.mail_provider_repository import MailProviderRepository
from locker_server.core.repositories.payment_repository import PaymentRepository
from locker_server.core.repositories.plan_repository import PlanRepository
from locker_server.shared.constants.transactions import *


class ResourceService:
    """
    This class represents Use Cases related Resource
    """

    def __init__(self, plan_repository: PlanRepository, country_repository: CountryRepository,
                 mail_provider_repository: MailProviderRepository,
                 payment_repository: PaymentRepository
                 ):
        self.plan_repository = plan_repository
        self.country_repository = country_repository
        self.mail_provider_repository = mail_provider_repository
        self.payment_repository = payment_repository

    def list_countries(self) -> List[Country]:
        return self.country_repository.list_countries()

    def list_personal_plans(self) -> List[PMPlan]:
        return self.plan_repository.list_plans(**{
            "exclude_alias": [PLAN_TYPE_PM_LIFETIME, PLAN_TYPE_PM_LIFETIME_FAMILY],
            "is_team_plan": False
        })

    def list_enterprise_plans(self) -> List[PMPlan]:
        return self.plan_repository.list_plans(**{
            "is_team_plan": True
        })

    def list_mail_providers(self) -> List[MailProvider]:
        return self.mail_provider_repository.list_mail_providers()

    def list_all_plans(self) -> List[PMPlan]:
        return self.plan_repository.list_plans()

    def list_individual_plans(self) -> List[PMPlan]:
        return self.plan_repository.list_plans(**{
            "is_team_plan": False
        })

    def list_payment_sources(self) -> List[Dict]:
        saas_markets = self.payment_repository.list_saas_market()
        for saas_market in saas_markets:
            saas_market.update({
                "id": saas_market.get("name")
            })
        payment_sources = [
            {
                "id": "stripe",
                "name": "Stripe"
            },
            {
                "id": "ios",
                "name": "App Store"

            },
            {
                "id": "android",
                "name": "Google Play"

            }
        ]
        return payment_sources + saas_markets
