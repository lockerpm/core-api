from rest_framework import serializers

from locker_server.shared.constants.backup_credential import LIST_CREDENTIAL_TYPE, CREDENTIAL_TYPE_HMAC, \
    WEBAUTHN_VALID_TRANSPORTS


class PasswordlessCredentialSerializer(serializers.Serializer):
    credential_id = serializers.CharField(max_length=255)
    random = serializers.CharField(max_length=64, required=False, allow_null=True, allow_blank=True)
    transports = serializers.ListSerializer(
        child=serializers.CharField(max_length=64, required=True), required=False, allow_empty=True, allow_null=True
    )
    name = serializers.CharField(max_length=255, allow_blank=False)
    type = serializers.ChoiceField(choices=LIST_CREDENTIAL_TYPE, required=False, default=CREDENTIAL_TYPE_HMAC)

    def validate(self, data):
        transports = data.get("transports")
        if transports and not any(valid_transport in transports for valid_transport in WEBAUTHN_VALID_TRANSPORTS):
            raise serializers.ValidationError(detail={"transports": ["The transports is not valid"]})
        data["transports"] = ",".join(transports) if transports else None
        return data
