from locker_server.core.entities.cipher.cipher import Cipher


class CipherHistory(object):
    def __init__(self, cipher_history_id: str, creation_date: float = None, revision_date: float = None,
                 last_use_date: float = None, reprompt: int = 0,
                 score: float = 0, data: str = None, cipher: Cipher = None):
        self._cipher_history_id = cipher_history_id
        self._creation_date = creation_date
        self._revision_date = revision_date
        self._last_use_date = last_use_date
        self._reprompt = reprompt
        self._score = score
        self._data = data
        self._cipher = cipher

    @property
    def cipher_history_id(self):
        return self._cipher_history_id

    @property
    def creation_date(self):
        return self._creation_date

    @property
    def revision_date(self):
        return self._revision_date

    @property
    def last_use_date(self):
        return self._last_use_date

    @property
    def reprompt(self):
        return self._reprompt

    @property
    def score(self):
        return self._score

    @property
    def data(self):
        return self._data

    @property
    def cipher(self):
        return self._cipher
