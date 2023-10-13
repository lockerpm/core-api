import json
from typing import Optional, List

import requests

from locker_server.core.entities.sso_configuration.sso_configuration import SSOConfiguration
from locker_server.core.exceptions.sso_configuration_exception import SSOConfigurationIdentifierExistedException, \
    SSOConfigurationDoesNotExistException
from locker_server.core.exceptions.user_exception import UserDoesNotExistException
from locker_server.core.repositories.sso_configuration_repository import SSOConfigurationRepository
from locker_server.core.repositories.user_repository import UserRepository
from locker_server.shared.constants.sso_provider import SSO_PROVIDER_OIDC
from locker_server.shared.external_services.requester.retry_requester import requester
from locker_server.shared.log.cylog import CyLog


class SSOConfigurationService:
    """
    Organization SSO configuration Use cases
    """

    def __init__(self, sso_configuration_repository: SSOConfigurationRepository, user_repository: UserRepository):
        self.sso_configuration_repository = sso_configuration_repository
        self.user_repository = user_repository

    def list_sso_configurations(self, **filters) -> List[SSOConfiguration]:
        return self.sso_configuration_repository.list_sso_configurations(**filters)

    def get_sso_configuration(self, sso_configuration_id: str) -> Optional[SSOConfiguration]:
        return self.sso_configuration_repository.get_sso_configuration(
            sso_configuration_id=sso_configuration_id
        )

    def get_sso_configuration_by_identifier(self, identifier: str) -> Optional[SSOConfiguration]:
        org_sso_config = self.sso_configuration_repository.get_sso_configuration_by_identifier(
            identifier=identifier
        )
        if not org_sso_config:
            raise SSOConfigurationDoesNotExistException
        return org_sso_config

    def update_sso_configuration(self, sso_configuration_id: str, sso_config_update_data) -> Optional[SSOConfiguration]:
        identifier = sso_config_update_data.get("identifier")
        if identifier:
            existed_sso_configuration = self.sso_configuration_repository.get_sso_configuration_by_identifier(
                identifier=identifier
            )
            if existed_sso_configuration and existed_sso_configuration.sso_configuration_id != sso_configuration_id:
                raise SSOConfigurationIdentifierExistedException
        updated_sso_configuration = self.sso_configuration_repository.update_sso_configuration(
            sso_configuration_id=sso_configuration_id, sso_config_update_data=sso_config_update_data
        )
        if not updated_sso_configuration:
            raise SSOConfigurationDoesNotExistException
        return updated_sso_configuration

    def create_sso_configuration(self, user_id: int, sso_config_create_data) -> SSOConfiguration:
        user = self.user_repository.get_user_by_id(user_id=user_id)
        if not user:
            raise UserDoesNotExistException
        # TODO: check permission of user
        identifier = sso_config_create_data.get("identifier")
        existed_sso_configuration = self.sso_configuration_repository.get_sso_configuration_by_identifier(
            identifier=identifier
        )
        if existed_sso_configuration:
            raise SSOConfigurationIdentifierExistedException
        sso_config_create_data.update({
            "created_by_id": user.user_id
        })
        return self.sso_configuration_repository.create_sso_configuration(
            sso_config_create_data=sso_config_create_data
        )

    def get_user_from_sso_configuration(self, sso_identifier: str, auth_token: str):
        sso_configuration = self.sso_configuration_repository.get_sso_configuration_by_identifier(
            identifier=sso_identifier
        )
        if not sso_configuration:
            raise SSOConfigurationDoesNotExistException
        sso_provider_id = sso_configuration.sso_provider.sso_provider_id
        if sso_provider_id == SSO_PROVIDER_OIDC:
            userinfo_endpoint = sso_configuration.sso_provider_options.get("userinfo_endpoint")
            try:
                headers = {'Authorization': f"Bearer {auth_token}"}
                res = requester(method="GET", url=userinfo_endpoint, headers=headers)
                if res.status_code == 200:
                    try:
                        user_info = res.json()
                        return user_info

                    except json.JSONDecodeError:
                        CyLog.error(
                            **{
                                "message": f"[!] User.get_from_sso_configuration JSON Decode error: {sso_identifier} {res.text}"
                            }
                        )
                        return {}
                return {}
            except (requests.RequestException, requests.ConnectTimeout):
                return {}
        return {}

    def get_first(self) -> SSOConfiguration:
        return self.sso_configuration_repository.get_first()
