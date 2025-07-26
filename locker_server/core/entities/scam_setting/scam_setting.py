from locker_server.api_orm.models import ScamSettingORM
from locker_server.core.entities.scam_setting.scam_setting_category import ScamSettingCategory
from locker_server.core.entities.user.user import User


class ScamSetting(object):
    def __init__(self, scam_setting_id: str, user: User, category: ScamSettingCategory, enabled: bool,
                 created_at: float = None, updated_at: float = None):
        self._scam_setting_id = scam_setting_id
        self._user = user
        self._category = category
        self._enabled = enabled
        self._created_at = created_at
        self._updated_at = updated_at

    @property
    def scam_setting_id(self) -> str:
        return self._scam_setting_id

    @property
    def user(self) -> User:
        return self._user

    @property
    def category(self) -> ScamSettingCategory:
        return self._category

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def created_at(self) -> float:
        return self._created_at

    @property
    def updated_at(self) -> float:
        return self._updated_at
