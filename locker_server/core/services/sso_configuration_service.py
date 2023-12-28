import json
import traceback
from typing import Optional, List

import requests

from locker_server.core.entities.sso_configuration.sso_configuration import SSOConfiguration
from locker_server.core.exceptions.sso_configuration_exception import SSOConfigurationIdentifierExistedException, \
    SSOConfigurationDoesNotExistException
from locker_server.core.exceptions.user_exception import UserDoesNotExistException
from locker_server.core.repositories.sso_configuration_repository import SSOConfigurationRepository
from locker_server.core.repositories.user_repository import UserRepository
from locker_server.shared.constants.sso_provider import SSO_PROVIDER_OAUTH2
from locker_server.shared.external_services.requester.retry_requester import requester
from locker_server.shared.log.cylog import CyLog


class SSOConfigurationService:
    """
    Organization SSO configuration Use cases
    """

    def __init__(self, sso_configuration_repository: SSOConfigurationRepository, user_repository: UserRepository):
        self.sso_configuration_repository = sso_configuration_repository
        self.user_repository = user_repository

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

    def update_sso_configuration(self, user_id: int, sso_config_update_data) -> Optional[SSOConfiguration]:
        user = self.user_repository.get_user_by_id(user_id=user_id)
        if not user:
            raise UserDoesNotExistException
        sso_config_update_data.update({
            "created_by_id": user.user_id
        })
        updated_sso_configuration = self.sso_configuration_repository.update_sso_configuration(
            sso_config_update_data=sso_config_update_data
        )
        return updated_sso_configuration

    def destroy_sso_configuration(self):
        return self.sso_configuration_repository.destroy_sso_configuration()

    def get_user_by_code(self, sso_identifier: str, code: str, redirect_uri: str = None, proxies=None):
        if sso_identifier:
            sso_configuration = self.sso_configuration_repository.get_sso_configuration_by_identifier(
                identifier=sso_identifier
            )
        else:
            sso_configuration = self.get_first()
        if not sso_configuration:
            CyLog.debug(**{"message": "[!] Not sso configuration"})
            return {}
        sso_provider_id = sso_configuration.sso_provider.sso_provider_id
        if sso_provider_id == SSO_PROVIDER_OAUTH2:
            sso_options = sso_configuration.sso_provider_options
            token_endpoint = sso_options.get("token_endpoint")
            userinfo_endpoint = sso_options.get("userinfo_endpoint")
            try:
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                token_data = {
                    "grant_type": "authorization_code",
                    "redirect_uri": sso_options.get("redirect_uri") or redirect_uri,
                    "client_id": sso_options.get("client_id"),
                    "client_secret": sso_options.get("client_secret"),
                    "code": code
                }
                res = requester(
                    method="POST", url=token_endpoint, headers=headers, data_send=token_data, is_json=False, timeout=10,
                    proxies=proxies
                )
                # res = requests.post(url=token_endpoint, headers=headers, data=token_data, timeout=10)

                # res = requester(method="GET", url=token_endpoint)
                if res.status_code == 200:
                    access_token = res.json().get("access_token")
                    token_type = res.json().get("token_type")
                else:
                    CyLog.debug(**{"message": f"[!] Get token error:::{res.status_code} - {res.text}"})
                    return {}
                user_res_header = {'Authorization': f"{token_type} {access_token}"}
                user_res = requester(
                    method="GET", url=userinfo_endpoint, headers=user_res_header, timeout=5, proxies=proxies
                )
                if user_res.status_code == 200:
                    try:
                        user_info = user_res.json()
                    except json.JSONDecodeError:
                        CyLog.error(**{
                            "message": f"[!] User.get_from_sso_configuration JSON Decode error: "
                                       f"{sso_configuration.identifier} {res.text}"
                        })
                        return {}
                    user_data = user_info.copy()
                    user_data["name"] = user_info.get(sso_options.get("name_claim_types") or "name")
                    user_data["email"] = user_info.get(sso_options.get("email_claim_types") or "email")
                    return user_data

            except (requests.RequestException, requests.ConnectTimeout):
                tb = traceback.format_exc()
                CyLog.debug(**{"message": f"[!] Get user timeout:::\n{tb}"})
                return {}
        CyLog.debug(**{"message": f"[!] Not found sso_provider_id"})
        return {}

    def get_first(self) -> Optional[SSOConfiguration]:
        return self.sso_configuration_repository.get_first()
