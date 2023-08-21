from locker_server.core.entities.enterprise.enterprise import Enterprise


class EnterprisePolicy(object):
    def __init__(self, policy_id: int, enterprise: Enterprise, policy_type: str,  enabled: bool = False):
        self._policy_id = policy_id
        self._enterprise = enterprise
        self._policy_type = policy_type
        self._enabled = enabled

    @property
    def policy_id(self):
        return self._policy_id

    @property
    def enterprise(self):
        return self._enterprise

    @property
    def policy_type(self):
        return self._policy_type

    @property
    def enabled(self):
        return self._enabled

