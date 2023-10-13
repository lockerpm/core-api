from typing import Optional, List
from abc import ABC, abstractmethod

from locker_server.core.entities.sso_configuration.sso_configuration import SSOConfiguration


class SSOConfigurationRepository(ABC):

    # ------------------------ List SSOConfiguration resource ------------------- #
    @abstractmethod
    def list_sso_configurations(self, **filters) -> List[SSOConfiguration]:
        pass

    # ------------------------ Get SSOConfiguration resource --------------------- #
    @abstractmethod
    def get_first(self) -> Optional[SSOConfiguration]:
        pass

    @abstractmethod
    def get_sso_configuration(self, sso_configuration_id: str) -> Optional[SSOConfiguration]:
        pass

    @abstractmethod
    def get_sso_configuration_by_identifier(self, identifier: str) -> Optional[SSOConfiguration]:
        pass

    # ------------------------ Create SSOConfiguration resource --------------------- #
    @abstractmethod
    def create_sso_configuration(self, sso_config_create_data) -> SSOConfiguration:
        pass

    # ------------------------ Update SSOConfiguration resource --------------------- #
    @abstractmethod
    def update_sso_configuration(self, sso_configuration_id: str, sso_config_update_data) -> SSOConfiguration:
        pass

    # ------------------------ Delete OrganizationSSOConfiguration resource --------------------- #
    @abstractmethod
    def destroy_sso_configuration(self, organization_id: str):
        pass
