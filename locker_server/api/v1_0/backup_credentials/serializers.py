from rest_framework import serializers

from locker_server.core.entities.user.backup_credential import BackupCredential
from locker_server.shared.constants.account import DEFAULT_KDF_MEMORY, DEFAULT_KDF_PARALLELISM
from locker_server.shared.constants.backup_credential import LIST_CREDENTIAL_TYPE, CREDENTIAL_TYPE_HMAC, \
    WEBAUTHN_VALID_TRANSPORTS
from locker_server.shared.constants.ciphers import KDF_TYPE, KDF_TYPE_ARGON2ID


class ListBackupCredentialSerializer(serializers.Serializer):
    def to_representation(self, instance: BackupCredential):
        data = {
            "id": instance.backup_credential_id,
            "master_password_hint": instance.master_password_hint,
            "creation_date": instance.creation_date,
            "key": instance.key,
            "fd_credential_id": instance.fd_credential_id,
            "fd_random": instance.fd_random,
            "fd_transports": instance.fd_transports,
            "name": instance.name,
            "type": instance.type,
            "last_use_date": instance.last_use_date,
            "kdf_version": instance.user.get_kdf_version(),
            "kdf": instance.kdf,
            "kdf_iterations": instance.kdf_iterations,
            "kdf_memory": instance.kdf_memory,
            "kdf_parallelism": instance.kdf_parallelism,
        }
        return data


class DetailBackupCredentialSerializer(ListBackupCredentialSerializer):
    def to_representation(self, instance):
        return super().to_representation(instance)


class CreateBackupCredentialSerializer(serializers.Serializer):
    master_password_hash = serializers.CharField(allow_blank=False)
    master_password_hint = serializers.CharField(required=False, allow_blank=True, max_length=128)
    key = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    fd_credential_id = serializers.CharField(max_length=300, required=False, allow_blank=True, allow_null=True)
    fd_random = serializers.CharField(max_length=128, required=False, allow_blank=True, allow_null=True)
    fd_transports = serializers.ListSerializer(
        child=serializers.CharField(max_length=64, required=True), required=False, allow_empty=True, allow_null=True
    )
    name = serializers.CharField(max_length=255, required=False, allow_blank=False)
    type = serializers.ChoiceField(choices=LIST_CREDENTIAL_TYPE, required=False, default=CREDENTIAL_TYPE_HMAC)
    kdf = serializers.IntegerField(required=False)
    kdf_iterations = serializers.IntegerField(required=False)
    kdf_memory = serializers.IntegerField(required=False, allow_null=True)
    kdf_parallelism = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        transports = data.get("fd_transports")
        if transports and not any(valid_transport in transports for valid_transport in WEBAUTHN_VALID_TRANSPORTS):
            raise serializers.ValidationError(detail={"transports": ["The transports is not valid"]})
        data["fd_transports"] = ",".join(transports) if transports else None

        kdf_iterations = data.get("kdf_iterations")
        if kdf_iterations and (kdf_iterations < 1 or kdf_iterations > 1000000):
            raise serializers.ValidationError(detail={
                "kdf_iterations": ["KDF iterations must be between 1 and 1000000"]
            })
        kdf_type = data.get("kdf")
        if kdf_type and not KDF_TYPE.get(kdf_type):
            raise serializers.ValidationError(detail={"kdf": ["This KDF Type is not valid"]})
        kdf_memory = data.get("kdf_memory")
        kdf_parallelism = data.get("kdf_parallelism")
        if kdf_type and kdf_type == KDF_TYPE_ARGON2ID:
            if not kdf_memory:
                data["kdf_memory"] = DEFAULT_KDF_MEMORY
            if not kdf_parallelism:
                data["kdf_parallelism"] = DEFAULT_KDF_PARALLELISM
        return data
