import ast
from typing import List

from locker_server.core.entities.user.user import User


class BackupCredential(object):
    def __init__(self, backup_credential_id: str, user: User,
                 master_password: str = None, master_password_hint: str = "", key: str = None,
                 public_key: str = None, private_key: str = None, creation_date: float = 0,
                 fd_credential_id: str = None, fd_random: str = None, fd_transports: List[str] = None,
                 kdf: int = 0, kdf_iterations: int = 0,
                 name: str = None, last_use_date: float = None, type: str = None
                 ):
        self._backup_credential_id = backup_credential_id
        self._creation_date = creation_date
        self._master_password = master_password
        self._master_password_hint = master_password_hint
        self._key = key
        self._public_key = public_key
        self._private_key = private_key
        self._fd_credential_id = fd_credential_id
        self._fd_random = fd_random
        self._fd_transports = fd_transports
        self._kdf_iterations = kdf_iterations
        self._kdf = kdf
        self._user = user
        self._name = name
        self._type = type
        self._last_use_date = last_use_date

    @property
    def backup_credential_id(self):
        return self._backup_credential_id

    @property
    def creation_date(self):
        return self._creation_date

    @property
    def master_password(self):
        return self._master_password

    @property
    def master_password_hint(self):
        return self._master_password_hint

    @property
    def key(self):
        return self._key

    @property
    def public_key(self):
        return self._public_key

    @property
    def private_key(self):
        return self._private_key

    @property
    def fd_credential_id(self):
        return self._fd_credential_id

    @property
    def fd_random(self):
        return self._fd_random

    @property
    def fd_transports(self):
        return self._fd_transports or []

    @property
    def user(self):
        return self._user

    @property
    def kdf_iterations(self):
        return self._kdf_iterations

    @property
    def kdf(self):
        return self._kdf

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def last_use_date(self):
        return self._last_use_date
