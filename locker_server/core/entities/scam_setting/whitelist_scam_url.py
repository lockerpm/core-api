from locker_server.core.entities.user.user import User


class WhitelistScamUrl(object):
    def __init__(self, whitelist_id: str, url: str, user: User, created_at: float, updated_at: float = None):
        self._whitelist_id = whitelist_id
        self._url = url
        self._user = user
        self._created_at = created_at
        self._updated_at = updated_at

    @property
    def whitelist_scam_url_id(self) -> str:
        return self._whitelist_id

    @property
    def url(self) -> str:
        return self._url

    @property
    def user(self) -> User:
        return self._user

    @property
    def created_at(self) -> float:
        return self._created_at

    @property
    def updated_at(self) -> float:
        return self._updated_at
