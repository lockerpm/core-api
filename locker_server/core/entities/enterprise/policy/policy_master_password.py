from locker_server.core.entities.enterprise.enterprise import Enterprise
from locker_server.core.entities.enterprise.policy.policy import EnterprisePolicy


class PolicyMasterPassword(EnterprisePolicy):
    def __init__(self, policy_id: int, enterprise: Enterprise, policy_type: str, enabled: bool = False,
                 min_length: int = None, require_lower_case: bool = False, require_upper_case: bool = False,
                 require_special_character: bool = False, require_digit: bool = False):
        super().__init__(policy_id=policy_id, enterprise=enterprise, policy_type=policy_type, enabled=enabled)
        self._min_length = min_length
        self._require_lower_case = require_lower_case
        self._require_upper_case = require_upper_case
        self._require_special_character = require_special_character
        self._require_digit = require_digit

    @property
    def min_length(self):
        return self._min_length

    @property
    def require_lower_case(self):
        return self._require_lower_case

    @property
    def require_upper_case(self):
        return self._require_upper_case

    @property
    def require_special_character(self):
        return self._require_special_character

    @property
    def require_digit(self):
        return self._require_digit
