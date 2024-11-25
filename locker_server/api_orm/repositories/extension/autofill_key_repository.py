from typing import Union, Dict, Optional, List
from abc import ABC, abstractmethod

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.extensions.autofill_keys import AutofillKeyORM
from locker_server.core.entities.extension.autofill_key import AutofillKey
from locker_server.core.repositories.extension.autofill_key_repository import AutofillKeyRepository
from locker_server.shared.utils.app import now

ModelParser = get_model_parser()


class AutofillKeyORMRepository(AutofillKeyRepository):
    # ------------------------ List AutofillKey resource ------------------- #

    def list_autofill_keys(self, **filters) -> List[AutofillKey]:
        list_autofill_orm = AutofillKeyORM.objects.all()
        return [
            ModelParser.extension_parser().parse_autofill_key(autofill) for autofill in list_autofill_orm
        ]

    # ------------------------ Get AutofillKey resource --------------------- #

    def get_autofill_key(self, key: str) -> Optional[AutofillKey]:
        try:
            autofill_orm = AutofillKeyORM.objects.get(key=key)
        except AutofillKeyORM.DoesNotExist:
            return None
        return ModelParser.extension_parser().parse_autofill_key(autofill_orm)

    # ------------------------ Create AutofillKey resource --------------------- #

    def create_autofill_key(self, **create_data) -> AutofillKey:
        key = create_data.get("key")
        values = create_data.get('values')
        autofill_orm, is_created = AutofillKeyORM.objects.get_or_create(
            key=key,
            defaults={
                "key": key,
                "values": values,
                "created_time": now(),

            }
        )
        if not is_created:
            # TODO: update key
            pass

        return ModelParser.extension_parser().parser_autofill_key(autofill_orm)

    # ------------------------ Update AutofillKey resource --------------------- #

    def update_autofill_key(self, key: str, **update_data) -> AutofillKey:
        autofill_orm, is_updated = AutofillKeyORM.objects.update_or_create(
            key=key,
            defaults={
                "key": key,
                "values": update_data.get("values")
            }
        )
        if is_updated:
            autofill_orm.updated_time = now()
            autofill_orm.save()
        return ModelParser.extension_parser().parse_autofill_key(autofill_orm)

    # ------------------------ Delete AutofillKey resource --------------------- #
    def delete_autofill_key(self, key: str) -> bool:
        autofill_orm = AutofillKeyORM.objects.filter(key=key).delete()
        return True
