from rest_framework import serializers

from locker_server.shared.constants.backup_credential import LIST_CREDENTIAL_TYPE


class PasswordlessCredentialSerializer(serializers.Serializer):
    credential_id = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255, allow_blank=False)
    type = serializers.ChoiceField(choices=LIST_CREDENTIAL_TYPE, required=False)
