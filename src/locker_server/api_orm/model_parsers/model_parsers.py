from .user_parsers import UserParser
from .user_plan_parsers import UserPlanParser
from .payment_parsers import PaymentParser
from .enterprise_parser import EnterpriseParser
from .event_parsers import EventParser


class ModelParser:
    """
    Parse ORM objects to Entities
    """

    @classmethod
    def user_parser(cls):
        return UserParser

    @classmethod
    def user_plan_parser(cls):
        return UserPlanParser

    @classmethod
    def payment_parser(cls):
        return PaymentParser

    @classmethod
    def enterprise_parser(cls):
        return EnterpriseParser

    @classmethod
    def event_parser(cls):
        return EventParser
