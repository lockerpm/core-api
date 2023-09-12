from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_cipher_model, get_folder_model, get_collection_cipher_model, \
    get_team_model, get_collection_member_model
from locker_server.api_orm.utils.revision_date import bump_account_revision_date
from locker_server.core.entities.cipher.cipher import Cipher
from locker_server.core.entities.cipher.folder import Folder
from locker_server.core.entities.member.team_member import TeamMember
from locker_server.core.entities.user.device import Device
from locker_server.core.entities.user.user import User
from locker_server.core.repositories.cipher_repository import CipherRepository
from locker_server.shared.constants.ciphers import CIPHER_TYPE_MASTER_PASSWORD
from locker_server.shared.constants.members import MEMBER_ROLE_OWNER, MEMBER_ROLE_ADMIN
from locker_server.shared.utils.app import now, diff_list


TeamORM = get_team_model()
CipherORM = get_cipher_model()
CollectionCipherORM = get_collection_cipher_model()
CollectionMemberORM = get_collection_member_model()
FolderORM = get_folder_model()
ModelParser = get_model_parser()


class CipherORMRepository(CipherRepository):
    @staticmethod
    def _get_cipher_orm(cipher_id: str) -> Optional[CipherORM]:
        try:
            cipher_orm = CipherORM.objects.get(id=cipher_id)
            return cipher_orm
        except CipherORM.DoesNotExist:
            return None

    # ------------------------ List Cipher resource ------------------- #
    def get_by_id(self, cipher_id: str) -> Optional[Cipher]:
        cipher_orm = self._get_cipher_orm(cipher_id=cipher_id)
        if not cipher_orm:
            return None
        return ModelParser.cipher_parser().parse_cipher(cipher_orm=cipher_orm)

    def list_cipher_collection_ids(self, cipher_id: str) -> List[str]:
        return list(CollectionCipherORM.objects.filter(cipher_id=cipher_id).values_list('collection_id', flat=True))

    # ------------------------ Get Cipher resource --------------------- #
    def get_user_folder(self, user_id: int, folder_id: str) -> Optional[Folder]:
        try:
            folder_orm = FolderORM.objects.get(user_id=user_id, id=folder_id)
        except FolderORM.DoesNotExist:
            return None
        return ModelParser.cipher_parser().parse_folder(folder_orm=folder_orm)

    def count_ciphers_created_by_user(self, user_id: int, **filter_params) -> int:
        ciphers = CipherORM.objects.filter(created_by_id=user_id)
        type_param = filter_params.get("type")
        if type_param:
            ciphers = ciphers.filter(type=type_param)
        return ciphers.count()

    def get_master_pwd_item(self, user_id: int) -> Optional[Cipher]:
        master_pwd_item = CipherORM.objects.filter(created_by_id=user_id, type=CIPHER_TYPE_MASTER_PASSWORD).first()
        return ModelParser.cipher_parser().parse_cipher(cipher_orm=master_pwd_item) if master_pwd_item else None

    def check_member_belongs_cipher_collections(self, cipher: Cipher, member: TeamMember) -> bool:
        cipher_collection_ids = self.list_cipher_collection_ids(cipher_id=cipher.cipher_id)
        member_collection_ids = list(
            CollectionMemberORM.objects.filter(member_id=member.team_member_id).values_list('collection_id', flat=True)
        )
        return any(collection_id in cipher_collection_ids for collection_id in member_collection_ids)

    # ------------------------ Create Cipher resource --------------------- #
    def create_cipher(self, cipher_data: Dict) -> Cipher:
        favorite = cipher_data.get("favorite", False)
        folder_id = cipher_data.get("folder_id", None)
        user_created_id = cipher_data.get("user_id")
        created_by_id = cipher_data.get("created_by_id")
        user_cipher_id = cipher_data.get("user_id")
        team_id = cipher_data.get("team_id")
        collection_ids = cipher_data.get("collection_ids", [])
        # If team_id is not null => This cipher belongs to team
        if team_id:
            user_cipher_id = None
        # Create new cipher object
        cipher_orm = CipherORM(
            creation_date=cipher_data.get("creation_date", now()),
            revision_date=cipher_data.get("revision_date", now()),
            deleted_date=cipher_data.get("deleted_date"),
            reprompt=cipher_data.get("reprompt", 0) or 0,
            score=cipher_data.get("score", 0),
            type=cipher_data.get("type"),
            data=cipher_data.get("data"),
            user_id=user_cipher_id,
            team_id=team_id,
            created_by_id=created_by_id,
        )
        cipher_orm.save()
        # Create CipherFavorite
        if user_created_id and favorite:
            cipher_orm.set_favorite(user_created_id, True)
        # Create CipherFolder
        if user_created_id and folder_id:
            cipher_orm.set_folder(user_created_id, folder_id)
        # Create CipherCollections
        if team_id:
            cipher_orm.collections_ciphers.model.create_multiple(cipher_orm.id, *collection_ids)

        # Update revision date of user (if this cipher is personal)
        # or all related cipher members (if this cipher belongs to a team)
        bump_account_revision_date(team=cipher_orm.team, **{
            "collection_ids": collection_ids,
            "role_name": [MEMBER_ROLE_OWNER, MEMBER_ROLE_ADMIN]
        })
        bump_account_revision_date(user=cipher_orm.user)
        return ModelParser.cipher_parser().parse_cipher(cipher_orm=cipher_orm)

    # ------------------------ Update Cipher resource --------------------- #
    def update_cipher(self, cipher_id: str, cipher_data: Dict) -> Cipher:
        cipher_orm = self._get_cipher_orm(cipher_id=cipher_id)
        user_created_id = cipher_data.get("user_id")
        user_cipher_id = cipher_data.get("user_id")
        team_id = cipher_data.get("team_id")
        collection_ids = cipher_data.get("collection_ids", [])

        # If team_id is not null => This cipher belongs to team
        if team_id:
            user_cipher_id = None
        # Create new cipher object
        cipher_orm.revision_date = now()
        cipher_orm.reprompt = cipher_data.get("reprompt", cipher_orm.reprompt) or 0
        cipher_orm.score = cipher_data.get("score", cipher_orm.score)
        cipher_orm.type = cipher_data.get("type", cipher_orm.type)
        cipher_orm.data = cipher_data.get("data", cipher_orm.get_data())
        cipher_orm.user_id = user_cipher_id
        cipher_orm.team_id = team_id
        cipher_orm.save()
        # Set favorite
        if user_created_id:
            favorite = cipher_data.get("favorite", cipher_orm.get_favorites().get(user_created_id, False))
            cipher_orm.set_favorite(user_id=user_created_id, is_favorite=favorite)

        # Set folder id
        folder_id = cipher_data.get("folder_id", cipher_orm.get_folders().get(user_created_id))
        cipher_orm.set_folder(user_created_id, folder_id)
        # Create CipherCollections
        if team_id:
            existed_collection_ids = list(cipher_orm.collections_ciphers.values_list('collection_id', flat=True))
            removed_collection_ids = diff_list(existed_collection_ids, collection_ids)
            added_collection_ids = diff_list(collection_ids, existed_collection_ids)
            cipher_orm.collections_ciphers.filter(collection_id__in=removed_collection_ids).delete()
            cipher_orm.collections_ciphers.model.create_multiple(cipher_orm.id, *added_collection_ids)
        else:
            cipher_orm.collections_ciphers.all().delete()

        # Update revision date of user (if this cipher is personal)
        # or all related cipher members (if this cipher belongs to a team)
        bump_account_revision_date(team=cipher_orm.team, **{
            "collection_ids": collection_ids,
            "role_name": [MEMBER_ROLE_OWNER, MEMBER_ROLE_ADMIN]
        })
        bump_account_revision_date(user=cipher_orm.user)

        return ModelParser.cipher_parser().parse_cipher(cipher_orm=cipher_orm)

    # ------------------------ Delete Cipher resource --------------------- #
    def delete_permanent_multiple_cipher_by_teams(self, team_ids):
        """
        Delete permanently ciphers by team ids
        :param team_ids:
        :return:
        """
        teams_orm = TeamORM.objects.filter(id__in=team_ids)
        CipherORM.objects.filter(team_id__in=team_ids).delete()
        for team_orm in teams_orm:
            bump_account_revision_date(team=team_orm)
