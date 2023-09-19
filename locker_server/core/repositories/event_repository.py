from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.enterprise.enterprise import Enterprise
from locker_server.core.entities.event.event import Event
from locker_server.core.entities.user.user import User


class EventRepository(ABC):
    # ------------------------ List Event resource ------------------- #

    # ------------------------ Get Event resource --------------------- #

    # ------------------------ Create Event resource --------------------- #
    @abstractmethod
    def create_new_event(self, **data) -> Event:
        pass

    @abstractmethod
    def create_new_event_by_multiple_teams(self, team_ids: list, **data):
        pass

    @abstractmethod
    def create_new_event_by_ciphers(self, ciphers, **data):
        pass

    # ------------------------ Update Event resource --------------------- #

    # ------------------------ Delete Event resource --------------------- #
