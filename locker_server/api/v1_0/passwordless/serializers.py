from rest_framework import serializers

from locker_server.shared.constants.backup_credential import LIST_CREDENTIAL_TYPE, CREDENTIAL_TYPE_HMAC


class PasswordlessCredentialSerializer(serializers.Serializer):
    credential_id = serializers.CharField(max_length=255)
    random = serializers.CharField(max_length=64, required=False, allow_null=True, allow_blank=True)
    name = serializers.CharField(max_length=255, allow_blank=False)
    type = serializers.ChoiceField(choices=LIST_CREDENTIAL_TYPE, required=False, default=CREDENTIAL_TYPE_HMAC)
