import json


class AutofillKey(object):
    def __init__(self, autofill_key_id: int, key: str, values: str = None,
                 created_time: float = None, updated_time: float = None):
        self._autofill_key_id = autofill_key_id
        self._key = key
        self._values = values
        self._created_time = created_time
        self._updated_time = updated_time

    @property
    def key(self) -> str:
        return self._key

    @property
    def values(self):
        try:
            self._values = self._values.replace('\'', "\"")
            return json.loads(self._values)
        except Exception as e:
            print(e)
            return self._values
