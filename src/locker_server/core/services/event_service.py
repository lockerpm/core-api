from typing import Tuple, Dict, List, Optional

from locker_server.core.entities.event.event import Event
from locker_server.core.repositories.event_repository import EventRepository


class EventService:
    """
    This class represents Use Cases related Event
    """

    def __init__(self, event_repository: EventRepository):
        self.event_repository = event_repository

    def create_new_event(self, **data) -> Event:
        return self.event_repository.create_new_event(**data)

    def create_new_event_by_multiple_teams(self, team_ids: list, **data):
        return self.create_new_event_by_multiple_teams(team_ids, **data)

    def create_new_event_by_ciphers(self, ciphers, **data):
        return self.create_new_event_by_ciphers(ciphers, **data)
