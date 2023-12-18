class AppInfo(object):
    def __init__(self, logo: str, name: str, creation_date: float, revision_date: float = 0):
        self._logo = logo
        self._name = name
        self._creation_date = creation_date
        self._revision_date = revision_date

    @property
    def logo(self):
        return self._logo

    @property
    def name(self):
        return self._name

    @property
    def creation_date(self):
        return self._creation_date

    @property
    def revision_date(self):
        return self._revision_date
