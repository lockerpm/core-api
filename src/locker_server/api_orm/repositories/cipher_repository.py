from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from django.db.models import Value, BooleanField, Q, Case, When, Count

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_cipher_model, get_folder_model, get_collection_cipher_model, \
    get_team_model, get_collection_member_model, get_team_member_model, get_user_model
from locker_server.api_orm.utils.revision_date import bump_account_revision_date
from locker_server.core.entities.cipher.cipher import Cipher
from locker_server.core.entities.cipher.folder import Folder
from locker_server.core.entities.member.team_member import TeamMember
from locker_server.core.entities.user.device import Device
from locker_server.core.entities.user.user import User
from locker_server.core.repositories.cipher_repository import CipherRepository
from locker_server.shared.constants.ciphers import CIPHER_TYPE_MASTER_PASSWORD, IMMUTABLE_CIPHER_TYPES
from locker_server.shared.constants.members import *
from locker_server.shared.utils.app import now, diff_list


UserORM = get_user_model()
TeamORM = get_team_model()
TeamMemberORM = get_team_member_model()
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

    @staticmethod
    def _get_user_orm(user_id: int) -> Optional[UserORM]:
        try:
            user_orm = UserORM.objects.get(user_id=user_id)
            return user_orm
        except UserORM.DoesNotExist:
            return None

    @staticmethod
    def _get_multiple_ciphers_orm_by_user(user_id: int, only_personal=False, only_managed_team=False,
                                          only_edited=False, only_deleted=False,
                                          exclude_team_ids=None, filter_ids=None, exclude_types=None):
        """
        Get list ciphers of user
        :param user_id: (int) The user id
        :param only_personal: (bool) if True => Only get list personal ciphers
        :param only_managed_team: (bool) if True => Only get list ciphers of non-locked teams
        :param only_edited: (bool) if True => Only get list ciphers that user is allowed edit permission
        :param only_deleted: (bool) if True => Only get list ciphers that user is allowed delete permission
        :param exclude_team_ids: (list) Excluding all ciphers have team_id in this list
        :param filter_ids: (list) List filtered cipher ids
        :param exclude_types: (list) Excluding all ciphers have type in this list
        :return:
        """
        if exclude_types is None:
            exclude_types = []
        personal_ciphers_orm = CipherORM.objects.filter(user_id=user_id)
        if filter_ids:
            personal_ciphers_orm = personal_ciphers_orm.filter(id__in=filter_ids)
        if only_personal is True:
            personal_ciphers_orm = personal_ciphers_orm.annotate(view_password=Value(True, output_field=BooleanField()))
            return personal_ciphers_orm

        confirmed_team_members_orm = TeamMemberORM.objects.filter(user_id=user_id, status=PM_MEMBER_STATUS_CONFIRMED)
        if only_managed_team:
            confirmed_team_members_orm = confirmed_team_members_orm.filter(team__locked=False)
        if exclude_team_ids:
            confirmed_team_members_orm = confirmed_team_members_orm.exclude(team_id__in=exclude_team_ids)

        confirmed_team_ids = confirmed_team_members_orm.values_list('team_id', flat=True)
        team_ciphers_orm = CipherORM.objects.filter(team_id__in=confirmed_team_ids)
        if filter_ids:
            team_ciphers_orm = team_ciphers_orm.filter(id__in=filter_ids)

        team_ciphers_orm = team_ciphers_orm.filter(
            # Owner, Admin ciphers
            Q(
                team__team_members__role_id__in=[MEMBER_ROLE_OWNER, MEMBER_ROLE_ADMIN],
                team__team_members__user_id=user_id
            ) |
            # Group access all ciphers
            Q(
                team__groups__access_all=True,
                team__groups__groups_members__member__user_id=user_id
            ) |
            # Team member
            Q(
                collections_ciphers__collection__collections_members__member__in=confirmed_team_members_orm,
                team__team_members__user_id=user_id
            ) |
            # Q(
            #     collections_ciphers__collection__collections_groups__group__groups_members__member__in=confirmed_team_members,
            #     team__team_members__user=user
            # ) |
            # Personal share
            Q(
                team__personal_share=True,
                team__team_members__user_id=user_id
            )
        ).distinct().annotate(
            view_password=Case(
                When(
                    Q(
                        team__team_members__role_id__in=[MEMBER_ROLE_MEMBER],
                        team__team_members__user_id=user_id,
                        collections_ciphers__collection__collections_members__hide_passwords=True
                    ), then=False
                ),
                When(
                    Q(
                        team__team_members__role_id__in=[MEMBER_ROLE_MEMBER],
                        team__team_members__user_id=user_id,
                        team__personal_share=True,
                        team__team_members__hide_passwords=True
                    ), then=False
                ),
                default=True,
                output_field=BooleanField()
            )
        )
        hide_password_cipher_ids = team_ciphers_orm.filter(view_password=False).values_list('id', flat=True)
        if only_edited:
            team_ciphers_orm = team_ciphers_orm.filter(
                team__team_members__role_id__in=[MEMBER_ROLE_OWNER, MEMBER_ROLE_ADMIN, MEMBER_ROLE_MANAGER],
                team__team_members__user_id=user_id
            )
        if only_deleted:
            team_ciphers_orm = team_ciphers_orm.filter(
                team__team_members__role_id__in=[MEMBER_ROLE_OWNER],
                team__team_members__user_id=user_id
            )
        return CipherORM.objects.filter(
            id__in=list(
                personal_ciphers_orm.values_list('id', flat=True)
            ) + list(team_ciphers_orm.values_list('id', flat=True))
        ).exclude(type__in=exclude_types).annotate(
            view_password=Case(
                When(id__in=hide_password_cipher_ids, then=False),
                default=True,
                output_field=BooleanField()
            )
        ).order_by('-revision_date')    # .prefetch_related('collections_ciphers')

    # ------------------------ List Cipher resource ------------------- #
    def list_cipher_collection_ids(self, cipher_id: str) -> List[str]:
        return list(CollectionCipherORM.objects.filter(cipher_id=cipher_id).values_list('collection_id', flat=True))

    def get_multiple_by_user(self, user_id: int, only_personal=False, only_managed_team=False,
                             only_edited=False, only_deleted=False,
                             exclude_team_ids=None, filter_ids=None, exclude_types=None) -> List[Cipher]:
        """
        Get list ciphers of user
        :param user_id: (int) The user id
        :param only_personal: (bool) if True => Only get list personal ciphers
        :param only_managed_team: (bool) if True => Only get list ciphers of non-locked teams
        :param only_edited: (bool) if True => Only get list ciphers that user is allowed edit permission
        :param only_deleted: (bool) if True => Only get list ciphers that user is allowed delete permission
        :param exclude_team_ids: (list) Excluding all ciphers have team_id in this list
        :param filter_ids: (list) List filtered cipher ids
        :param exclude_types: (list) Excluding all ciphers have type in this list
        :return:
        """

        ciphers_orm = self._get_multiple_ciphers_orm_by_user(
            user_id=user_id, only_personal=only_personal, only_managed_team=only_managed_team,
            only_edited=only_edited, only_deleted=only_deleted,
            exclude_team_ids=exclude_team_ids, filter_ids=filter_ids, exclude_types=exclude_types
        ).prefetch_related('collections_ciphers')
        return [ModelParser.cipher_parser().parse_cipher(cipher_orm=c, parse_collection_ids=True) for c in ciphers_orm]

    # ------------------------ Get Cipher resource --------------------- #
    def get_by_id(self, cipher_id: str) -> Optional[Cipher]:
        cipher_orm = self._get_cipher_orm(cipher_id=cipher_id)
        if not cipher_orm:
            return None
        return ModelParser.cipher_parser().parse_cipher(cipher_orm=cipher_orm)

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

    def sync_and_statistic_ciphers(self, user_id: int, only_personal=False, only_managed_team=False,
                                   only_edited=False, only_deleted=False,
                                   exclude_team_ids=None, filter_ids=None, exclude_types=None) -> Dict:
        ciphers_orm = self._get_multiple_ciphers_orm_by_user(
            user_id=user_id, only_personal=only_personal, only_managed_team=only_managed_team,
            only_edited=only_edited, only_deleted=only_deleted,
            exclude_team_ids=exclude_team_ids, filter_ids=filter_ids, exclude_types=exclude_types
        ).prefetch_related('collections_ciphers')
        total_cipher = ciphers_orm.count()
        not_deleted_ciphers_orm = ciphers_orm.filter(deleted_date__isnull=True)
        not_deleted_ciphers_statistic = not_deleted_ciphers_orm.values('type').annotate(
            count=Count('type')
        ).order_by('-count')
        not_deleted_ciphers_count = {item["type"]: item["count"] for item in list(not_deleted_ciphers_statistic)}
        return {
            "count": {
                "ciphers": total_cipher,
                "not_deleted_ciphers": {
                    "total": not_deleted_ciphers_orm.count(),
                    "ciphers": not_deleted_ciphers_count
                },
            },
            "ciphers": [
                ModelParser.cipher_parser().parse_cipher(cipher_orm=c, parse_collection_ids=True) for c in ciphers_orm
            ]
        }

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

    def update_folders(self, cipher_id: str, new_folders_data) -> Cipher:
        cipher_orm = self._get_cipher_orm(cipher_id=cipher_id)
        cipher_orm.folders = new_folders_data
        cipher_orm.save()
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

    def delete_multiple_cipher(self, cipher_ids: list, user_id_deleted: int):
        current_time = now()
        # Update deleted_date of the ciphers
        ciphers_orm = self._get_multiple_ciphers_orm_by_user(
            user_id=user_id_deleted, only_deleted=True
        ).filter(
            id__in=cipher_ids, deleted_date__isnull=True
        ).exclude(type__in=IMMUTABLE_CIPHER_TYPES)
        deleted_cipher_ids = list(ciphers_orm.values_list('id', flat=True))
        for cipher_orm in ciphers_orm:
            cipher_orm.revision_date = current_time
            cipher_orm.deleted_date = current_time
        CipherORM.objects.bulk_update(ciphers_orm, ['revision_date', 'deleted_date'], batch_size=100)

        # Bump revision date: teams and user
        team_ids = ciphers_orm.exclude(team__isnull=True).values_list('team_id', flat=True)
        teams_orm = TeamORM.objects.filter(id__in=team_ids)
        for team_orm in teams_orm:
            bump_account_revision_date(team=team_orm)
        bump_account_revision_date(user=self._get_user_orm(user_id=user_id_deleted))
        return deleted_cipher_ids
