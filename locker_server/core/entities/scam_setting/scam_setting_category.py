import json

from locker_server.core.entities.user.user import User
from locker_server.core.entities.user_reward.mission import Mission
from locker_server.shared.constants.missions import USER_MISSION_STATUS_NOT_STARTED


class ScamSettingCategory(object):
    def __init__(self, scam_setting_category_id: str, name: str, name_vi: str,
                 enable: bool):
        self._scam_setting_category_id = scam_setting_category_id
        self._name = name
        self._name_vi = name_vi
        self._enable = enable

    @property
    def scam_setting_category_id(self) -> str:
        return self._scam_setting_category_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def name_vi(self) -> str:
        return self._name_vi

    @property
    def enabled(self) -> bool:
        return self._enable
