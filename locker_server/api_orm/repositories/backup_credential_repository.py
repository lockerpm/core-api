from typing import Optional, Dict

from django.contrib.auth.hashers import make_password

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_backup_credential_model
from locker_server.core.entities.user.backup_credential import BackupCredential
from locker_server.core.repositories.backup_credential_repository import BackupCredentialRepository

BackupCredentialORM = get_backup_credential_model()
ModelParser = get_model_parser()


class BackupCredentialORMRepository(BackupCredentialRepository):
    # ------------------------ List BackupCredential resource ------------------- #
    def list_backup_credentials(self, **filters) -> [BackupCredential]:
        user_id_param = filters.get("user_id")
        if user_id_param:
            backup_credentials_orm = BackupCredentialORM.objects.filter(
                user_id=user_id_param
            ).order_by("id").select_related('user')
        else:
            backup_credentials_orm = BackupCredentialORM.objects.all().order_by("id").select_related('user')
        return [
            ModelParser.user_parser().parse_backup_credential(
                backup_credential_orm=backup_credential_orm
            )
            for backup_credential_orm in backup_credentials_orm
        ]

    def count_backup_credentials(self, **filters) -> int:
        user_id_param = filters.get("user_id")
        if user_id_param:
            backup_credentials_orm = BackupCredentialORM.objects.filter(
                user_id=user_id_param
            )
        else:
            backup_credentials_orm = BackupCredentialORM.objects.all()

        return backup_credentials_orm.count()

    # ------------------------ Get BackupCredential resource --------------------- #
    def get_by_id(self, backup_credential_id: str) -> Optional[BackupCredential]:
        try:
            backup_credential_orm = BackupCredentialORM.objects.get(
                id=backup_credential_id
            )
        except BackupCredentialORM.DoesNotExist:
            return None
        except ValueError:
            return None
        return ModelParser.user_parser().parse_backup_credential(backup_credential_orm=backup_credential_orm)

    # ------------------------ Create BackupCredential resource --------------------- #
    def create_backup_credential(self, backup_credential_create_data: Dict) -> Optional[BackupCredential]:
        backup_credential_orm = BackupCredentialORM.create(**backup_credential_create_data)
        return ModelParser.user_parser().parse_backup_credential(backup_credential_orm=backup_credential_orm)

    # ------------------------ Update BackupCredential resource --------------------- #
    def update_backup_credential(self, backup_credential_id: str, update_data: Dict) -> Optional[BackupCredential]:
        try:
            backup_credential_orm = BackupCredentialORM.objects.get(
                id=backup_credential_id
            )
        except BackupCredentialORM.DoesNotExist:
            return None
        raw_master_password = update_data.get("master_password") or update_data.get("master_password_hash")
        if raw_master_password is not None:
            backup_credential_orm.master_password = make_password(raw_master_password)
        if "key" in update_data:
            backup_credential_orm.key = update_data.get("key", backup_credential_orm.key)
        if "kdf" in update_data:
            backup_credential_orm.kdf = update_data.get("kdf", backup_credential_orm.kdf)
        if "kdf_iterations" in update_data:
            backup_credential_orm.kdf_iterations = update_data.get(
                "kdf_iterations", backup_credential_orm.kdf_iterations
            )
        if "kdf_memory" in update_data:
            backup_credential_orm.kdf_memory = update_data.get(
                "kdf_memory", backup_credential_orm.kdf_memory
            )
        if "kdf_parallelism" in update_data:
            backup_credential_orm.kdf_parallelism = update_data.get(
                "kdf_parallelism", backup_credential_orm.kdf_parallelism
            )
        if "master_password_hint" in update_data:
            backup_credential_orm.master_password_hint = update_data.get(
                "master_password_hint", backup_credential_orm.master_password_hint
            )
        backup_credential_orm.save()
        return ModelParser.user_parser().parse_backup_credential(backup_credential_orm=backup_credential_orm)

    # ------------------------ Delete BackupCredential resource --------------------- #
    def delete_backup_credential(self, backup_credential_id: str) -> bool:
        try:
            backup_credential_orm = BackupCredentialORM.objects.get(
                id=backup_credential_id
            )
        except BackupCredentialORM.DoesNotExist:
            return False
        backup_credential_orm.delete()
        return True
