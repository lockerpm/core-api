from typing import List, Optional

from locker_server.core.entities.release.release import Release
from locker_server.core.repositories.release_repository import ReleaseRepository


class ReleaseService:
    """
    This class represents Use Cases related release
    """

    def __init__(self, release_repository: ReleaseRepository):
        self.release_repository = release_repository

    def get_latest_release(self, client_id: str, environment: str) -> Optional[Release]:
        latest_release = self.release_repository.get_latest_release(
            client_id=client_id,
            environment=environment
        )
        return latest_release

    def create_release(self, release_create_data) -> Release:
        return self.release_repository.create_release(release_create_data=release_create_data)

    def create_next_release(self, client_id: str, environment: str) -> Optional[Release]:
        latest_release = self.get_latest_release(
            client_id=client_id,
            environment=environment
        )
        if not latest_release:
            return None
        if not latest_release.patch:
            next_minor = int(latest_release.minor) + 1
            release_create_data = {
                "major": latest_release.major,
                "minor": next_minor,
                "client_id": client_id,
                "environment": environment
            }
            return self.create_release(release_create_data=release_create_data)
        if not latest_release.build_number:
            next_patch = int(latest_release.patch) + 1
            release_create_data = {
                "major": latest_release.major,
                "minor": latest_release.minor,
                "patch": next_patch,
                "client_id": client_id,
                "environment": environment
            }
            return self.create_release(release_create_data=release_create_data)
        next_build_number = int(latest_release.build_number) + 1
        release_create_data = {
            "major": latest_release.major,
            "minor": latest_release.minor,
            "patch": latest_release.patch,
            "build_number": next_build_number,
            "client_id": client_id,
            "environment": environment
        }
        return self.create_release(release_create_data=release_create_data)
