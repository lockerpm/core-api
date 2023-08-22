from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_team_model, get_collection_model
from locker_server.core.entities.team.collection import Collection
from locker_server.core.repositories.team_repository import TeamRepository

TeamORM = get_team_model()
CollectionORM = get_collection_model()
ModelParser = get_model_parser()


class TeamORMRepository(TeamRepository):
    # ------------------------ List Team resource ------------------- #
    def list_team_collection_ids(self, team_id: str) -> List[str]:
        return list(CollectionORM.objects.filter(team_id=team_id).values_list('id', flat=True))

    # ------------------------ Get Team resource --------------------- #
    def get_default_collection(self, team_id: str) -> Optional[Collection]:
        try:
            collection_orm = CollectionORM.objects.get(team_id=team_id, is_default=True)
        except CollectionORM.DoesNotExist:
            return None
        return ModelParser.team_parser().parse_collection(collection_orm=collection_orm)

    # ------------------------ Create PMPlan resource --------------------- #

    # ------------------------ Update PMPlan resource --------------------- #

    # ------------------------ Delete PMPlan resource --------------------- #

