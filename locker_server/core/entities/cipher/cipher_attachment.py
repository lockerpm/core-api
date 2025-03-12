from locker_server.core.entities.cipher.cipher import Cipher


class CipherAttachment(object):
    def __init__(self, cipher_attachment_id: int, creation_date: float = None, path: str = None, file_name: str = None,
                 size: int = None, key: str = None, cipher: Cipher = None):
        self._cipher_attachment_id = cipher_attachment_id
        self._creation_date = creation_date
        self._path = path
        self._file_name = file_name
        self._size = size
        self._key = key
        self._cipher = cipher

    @property
    def cipher_attachmnet_id(self):
        return self._cipher_attachment_id

    @property
    def creation_date(self):
        return self._creation_date

    @property
    def path(self):
        return self._path

    @property
    def file_name(self):
        return self._file_name

    @property
    def size(self):
        return self._size

    @property
    def key(self):
        return self._key

    @property
    def cipher(self):
        return self._cipher
