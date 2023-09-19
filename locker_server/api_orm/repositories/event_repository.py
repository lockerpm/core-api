from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_user_model, get_enterprise_domain_model, \
    get_enterprise_member_model, get_enterprise_group_member_model, get_enterprise_model, get_event_model
from locker_server.core.entities.enterprise.enterprise import Enterprise
from locker_server.core.entities.event.event import Event
from locker_server.core.entities.user.user import User
from locker_server.core.repositories.enterprise_member_repository import EnterpriseMemberRepository
from locker_server.core.repositories.enterprise_repository import EnterpriseRepository
from locker_server.core.repositories.event_repository import EventRepository
from locker_server.shared.constants.enterprise_members import E_MEMBER_ROLE_MEMBER, E_MEMBER_STATUS_CONFIRMED
from locker_server.shared.constants.members import PM_MEMBER_STATUS_INVITED
from locker_server.shared.log.cylog import CyLog
from locker_server.shared.utils.network import extract_root_domain


EventORM = get_event_model()
ModelParser = get_model_parser()


class EventORMRepository(EventRepository):
    # ------------------------ List Enterprise resource ------------------- #

    # ------------------------ Get Enterprise resource --------------------- #

    # ------------------------ Create Enterprise resource --------------------- #
    def create_new_event(self, **data) -> Event:
        event_orm = EventORM.create(**data)


    def create_new_event_by_multiple_teams(self, team_ids: list, **data):
        pass

    def create_new_event_by_ciphers(self, ciphers, **data):
        pass

    # ------------------------ Update Enterprise resource --------------------- #

    # ------------------------ Delete Enterprise resource --------------------- #

