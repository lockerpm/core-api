from typing import Optional, List

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_sso_configuration_model
from locker_server.core.entities.sso_configuration.sso_configuration import SSOConfiguration
from locker_server.core.repositories.sso_configuration_repository import SSOConfigurationRepository
from locker_server.shared.utils.app import now

SSOConfigurationORM = get_sso_configuration_model()
ModelParser = get_model_parser()


class SSOConfigurationORMRepository(SSOConfigurationRepository):

    # ------------------------ List SSOConfiguration resource ------------------- #
    def list_sso_configurations(self, **filters) -> List[SSOConfiguration]:
        created_by_id_param = filters.get("created_by_id")
        if created_by_id_param:
            sso_configurations_orm = SSOConfigurationORM.objects.filter(
                created_by_id=created_by_id_param
            ).order_by('creation_date')
        else:
            sso_configurations_orm = SSOConfigurationORM.objects.all().order_by('creation_date')
        return [
            ModelParser.sso_configuration_parser().parse_sso_configuration(
                sso_configuration_orm=sso_configuration_orm
            )
            for sso_configuration_orm in sso_configurations_orm
        ]

    # ------------------------ Get SSOConfiguration resource --------------------- #
    def get_sso_configuration(self, sso_configuration_id: str) -> Optional[SSOConfiguration]:
        try:
            sso_configuration_orm = SSOConfigurationORM.objects.get(
                id=sso_configuration_id
            )
        except SSOConfigurationORM.DoesNotExist:
            return None
        return ModelParser.sso_configuration_parser().parse_sso_configuration(
            sso_configuration_orm=sso_configuration_orm
        )

    def get_sso_configuration_by_identifier(self, identifier: str) -> Optional[SSOConfiguration]:
        try:
            sso_configuration_orm = SSOConfigurationORM.objects.get(
                identifier=identifier
            )
        except SSOConfigurationORM.DoesNotExist:
            return None
        return ModelParser.sso_configuration_parser().parse_sso_configuration(
            sso_configuration_orm=sso_configuration_orm
        )

    # ------------------------ Create SSOConfiguration resource --------------------- #
    def create_sso_configuration(self, sso_config_create_data) -> SSOConfiguration:
        sso_configuration_orm = SSOConfigurationORM.create(**sso_config_create_data)
        return ModelParser.sso_configuration_parser().parse_sso_configuration(
            sso_configuration_orm=sso_configuration_orm
        )

        # ------------------------ Update SSOConfiguration resource --------------------- #

    def update_sso_configuration(self, sso_configuration_id: str, sso_config_update_data) -> Optional[SSOConfiguration]:
        try:
            sso_configuration_orm = SSOConfigurationORM.objects.get(id=sso_configuration_id)
        except SSOConfigurationORM.DoesNotExist:
            return None
        sso_provider_id = sso_config_update_data.get("sso_provider_id") or sso_config_update_data.get("sso_provider")
        sso_configuration_orm.sso_provider_id = sso_provider_id or sso_configuration_orm.sso_provider_id
        sso_configuration_orm.sso_provider_options = sso_config_update_data.get(
            "sso_provider_options", sso_configuration_orm.sso_provider_options
        )
        sso_configuration_orm.enabled = sso_config_update_data.get(
            "enabled", sso_configuration_orm.enabled
        )
        sso_configuration_orm.identifier = sso_config_update_data.get(
            "identifier", sso_configuration_orm.identifier
        )
        sso_configuration_orm.revision_date = now()

        sso_configuration_orm.save()
        return ModelParser.sso_configuration_parser().parse_sso_configuration(
            sso_configuration_orm=sso_configuration_orm
        )

    # ------------------------ Delete SSOConfiguration resource --------------------- #
    def destroy_sso_configuration(self, sso_configuration_id: str):
        pass
