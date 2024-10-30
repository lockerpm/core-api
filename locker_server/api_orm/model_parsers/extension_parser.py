from locker_server.api_orm.models.extensions.autofill_keys import AutofillKeyORM
from locker_server.core.entities.extension.autofill_key import AutofillKey


class ExtensionParser:
    @classmethod
    def parse_autofill_key(cls, autofill_orm: AutofillKeyORM) -> AutofillKey:
        return AutofillKey(
            autofill_key_id=autofill_orm.id,
            key=autofill_orm.key,
            values=autofill_orm.values,
            created_time=autofill_orm.created_time,
            updated_time=autofill_orm.updated_time,
        )
