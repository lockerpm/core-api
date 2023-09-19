from locker_server.api_orm.abstracts.releases.releases import AbstractReleaseORM
from locker_server.shared.constants.release import RELEASE_ENVIRONMENT_PROD
from locker_server.shared.utils.app import now


class ReleaseORM(AbstractReleaseORM):
    class Meta(AbstractReleaseORM.Meta):
        swappable = 'LS_RELEASE_MODEL'
        db_table = 'cs_releases'

    @classmethod
    def create(cls, **data):
        new_release = cls(
            created_time=now(),
            major=data.get("major"),
            minor=data.get("minor"),
            patch=data.get("patch", ""),
            build_number=data.get("build_number", ""),
            description_en=data.get("description_en", ""),
            client_id=data.get("client_id"),
            environment=data.get("environment", RELEASE_ENVIRONMENT_PROD)
        )
        new_release.save()
        return new_release
