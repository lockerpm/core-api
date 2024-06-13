from rest_framework import serializers

from locker_server.core.entities.user.backup_credential import BackupCredential
from locker_server.shared.constants.backup_credential import LIST_CREDENTIAL_TYPE, CREDENTIAL_TYPE_HMAC, \
    WEBAUTHN_VALID_TRANSPORTS


class ListBackupCredentialSerializer(serializers.Serializer):
    def to_representation(self, instance: BackupCredential):
        data = {
            "id": instance.backup_credential_id,
            "master_password_hint": instance.master_password_hint,
            "creation_date": instance.creation_date,
            "key": instance.key,
            "fd_credential_id": instance.fd_credential_id,
            "fd_random": instance.fd_random,
            "fd_transports": instance.fd_transports if instance.fd_transports else WEBAUTHN_VALID_TRANSPORTS,
            "name": instance.name,
            "type": instance.type,
            "last_use_date": instance.last_use_date
        }
        return data


class DetailBackupCredentialSerializer(ListBackupCredentialSerializer):
    def to_representation(self, instance):
        return super().to_representation(instance)


class CreateBackupCredentialSerializer(serializers.Serializer):
    master_password_hash = serializers.CharField(allow_blank=False)
    master_password_hint = serializers.CharField(required=False, allow_blank=True, max_length=128)
    key = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    fd_credential_id = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    fd_random = serializers.CharField(max_length=128, required=False, allow_blank=True, allow_null=True)
    fd_transports = serializers.ListSerializer(
        child=serializers.CharField(max_length=64, required=True), required=False, allow_empty=True, allow_null=True
    )
    name = serializers.CharField(max_length=255, required=False, allow_blank=False)
    type = serializers.ChoiceField(choices=LIST_CREDENTIAL_TYPE, required=False, default=CREDENTIAL_TYPE_HMAC)

    def validate(self, data):
        transports = data.get("fd_transports")
        if transports and not any(valid_transport in transports for valid_transport in WEBAUTHN_VALID_TRANSPORTS):
            raise serializers.ValidationError(detail={"transports": ["The transports is not valid"]})
        data["fd_transports"] = ",".join(transports) if transports else None
        return data
