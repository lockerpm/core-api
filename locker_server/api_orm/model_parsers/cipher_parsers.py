import ast
from typing import List

from locker_server.api_orm.model_parsers.wrapper_specific_model_parser import get_specific_model_parser
from locker_server.api_orm.models import *
from locker_server.core.entities.cipher.cipher import Cipher
from locker_server.core.entities.cipher.cipher_history import CipherHistory
from locker_server.core.entities.cipher.folder import Folder
from locker_server.shared.utils.app import convert_readable_date


class CipherParser:
    @classmethod
    def parse_cipher(cls, cipher_orm: CipherORM, parse_collection_ids=False, parse_histories=False,
                     limit_history: int = None) -> Cipher:
        user_parser = get_specific_model_parser("UserParser")
        team_parser = get_specific_model_parser("TeamParser")
        try:
            view_password = getattr(cipher_orm, "view_password")
        except AttributeError:
            view_password = True
        cipher = Cipher(
            cipher_id=cipher_orm.id,
            creation_date=cipher_orm.creation_date,
            revision_date=cipher_orm.revision_date,
            deleted_date=cipher_orm.deleted_date,
            last_use_date=cipher_orm.last_use_date,
            num_use=cipher_orm.num_use,
            reprompt=cipher_orm.reprompt,
            score=cipher_orm.score,
            cipher_type=cipher_orm.type,
            data=cipher_orm.get_data(),
            folders=cipher_orm.get_folders(),
            favorites=cipher_orm.get_favorites(),
            view_password=view_password,
            user=user_parser.parse_user(user_orm=cipher_orm.user) if cipher_orm.user else None,
            created_by=user_parser.parse_user(user_orm=cipher_orm.created_by) if cipher_orm.created_by else None,
            team=team_parser.parse_team(team_orm=cipher_orm.team) if cipher_orm.team else None,
        )
        if parse_collection_ids is True:
            collection_ids = []
            try:
                if cipher_orm.collections_ciphers.exists():
                    collection_ids = list(cipher_orm.collections_ciphers.values_list('collection_id', flat=True))
            except AttributeError:
                pass
            cipher.collection_ids = collection_ids

        if parse_histories is True:
            try:
                show_history = getattr(cipher_orm, "show_history")
            except AttributeError:
                show_history = True
            if show_history is False:
                cipher.history = []
            else:
                cipher.history = cls.parse_password_history(cipher_orm=cipher_orm, limit_history=limit_history)
        return cipher

    @classmethod
    def parse_password_history(cls, cipher_orm: CipherORM, limit_history: int = None) -> List:
        history = []
        histories_orm = cipher_orm.cipher_histories.order_by('creation_date').values('last_use_date', 'data')
        for history_orm in histories_orm:
            data = history_orm.get("data")
            data = {} if not data else ast.literal_eval(str(data))
            history.append({
                "last_used_date": convert_readable_date(history_orm.get("last_use_date")),
                "password": data.get("password")
            })
        if limit_history is not None:
            history = history[-limit_history:]
        return history

    @classmethod
    def parse_folder(cls, folder_orm: FolderORM) -> Folder:
        user_parser = get_specific_model_parser("UserParser")
        return Folder(
            folder_id=folder_orm.id,
            name=folder_orm.name,
            creation_date=folder_orm.creation_date,
            revision_date=folder_orm.revision_date,
            user=user_parser.parse_user(user_orm=folder_orm.user)
        )

    @classmethod
    def parse_cipher_history(cls, cipher_history_orm: CipherHistoryORM, parse_cipher=False) -> CipherHistory:
        cipher = None
        if parse_cipher is True:
            cipher = cls.parse_cipher(cipher_orm=cipher_history_orm.cipher)
        return CipherHistory(
            cipher_history_id=cipher_history_orm.id,
            creation_date=cipher_history_orm.creation_date,
            revision_date=cipher_history_orm.revision_date,
            last_use_date=cipher_history_orm.last_use_date,
            reprompt=cipher_history_orm.reprompt,
            score=cipher_history_orm.score,
            data=cipher_history_orm.get_data(),
            cipher=cipher,
        )
