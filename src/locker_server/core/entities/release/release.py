class Release(object):
    def __init__(self, release_id: int, created_time: int = None, major: str = None, minor: str = None,
                 patch: str = None, build_number: str = None, description_en: str = "", description_vi: str = "",
                 client_id: str = None, environment: str = "prod"):
        self._release_id = release_id
        self._created_time = created_time
        self._major = major
        self._minor = minor
        self._patch = patch
        self._build_number = build_number
        self._description_en = description_en
        self._description_vi = description_vi
        self._client_id = client_id
        self._environment = environment

    @property
    def release_id(self):
        return self._release_id

    @property
    def created_time(self):
        return self._created_time

    @property
    def major(self):
        return self._major

    @property
    def minor(self):
        return self._minor

    @property
    def patch(self):
        return self._patch

    @property
    def build_number(self):
        return self._build_number

    @property
    def description_en(self):
        return self._description_en

    @property
    def description_vi(self):
        return self._description_vi

    @property
    def client_id(self):
        return self._client_id

    @property
    def environment(self):
        return self._environment
