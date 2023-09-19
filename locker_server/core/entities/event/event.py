class Event(object):
    def __init__(self, event_id: str, event_type: str = None, acting_user_id: int = None, user_id: int = None,
                 cipher_id: str = None, collection_id: str = None, creation_date: float = None, device_type: int = None,
                 group_id: str = None, ip_address: str = None, team_id: str = None, team_member_id: str = None,
                 provider_id: str = None, policy_id: str = None, team_provider_id: str = None,
                 user_provider_id: str = None, metadata: str = None):
        self._event_id = event_id
        self._event_type = event_type
        self._acting_user_id = acting_user_id
        self._user_id = user_id
        self._cipher_id = cipher_id
        self._collection_id = collection_id
        self._creation_date = creation_date
        self._device_type = device_type
        self._group_id = group_id
        self._ip_address = ip_address
        self._team_id = team_id
        self._team_member_id = team_member_id
        self._policy_id = policy_id
        self._provider_id = provider_id
        self._team_provider_id = team_provider_id
        self._user_provider_id = user_provider_id
        self._metadata = metadata

    @property
    def event_id(self):
        return self._event_id

    @property
    def event_type(self):
        return self._event_type

    @property
    def acting_user_id(self):
        return self._acting_user_id

    @property
    def user_id(self):
        return self._user_id

    @property
    def cipher_id(self):
        return self._cipher_id

    @property
    def collection_id(self):
        return self._collection_id

    @property
    def creation_date(self):
        return self._creation_date

    @property
    def device_type(self):
        return self._device_type

    @property
    def group_id(self):
        return self._group_id

    @property
    def ip_address(self):
        return self._ip_address

    @property
    def team_id(self):
        return self._team_id

    @property
    def team_member_id(self):
        return self._team_member_id

    @property
    def policy_id(self):
        return self._policy_id

    @property
    def provider_id(self):
        return self._provider_id

    @property
    def team_provider_id(self):
        return self._team_provider_id

    @property
    def user_provider_id(self):
        return self._user_provider_id

    @property
    def metadata(self):
        return self._metadata
