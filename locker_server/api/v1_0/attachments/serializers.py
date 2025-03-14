from rest_framework import serializers

from locker_server.shared.constants.attachments import UPLOAD_ACTION_ATTACHMENT


class AttachmentUploadMetadataSerializer(serializers.Serializer):
    cipher_id = serializers.CharField(max_length=64, required=False, allow_null=True)


class AttachmentUploadSerializer(serializers.Serializer):
    file_name = serializers.CharField(max_length=255)
    action = serializers.ChoiceField(
        choices=[UPLOAD_ACTION_ATTACHMENT],
        default=UPLOAD_ACTION_ATTACHMENT
    )
    metadata = AttachmentUploadMetadataSerializer(many=False, required=False)

    def validate(self, data):
        action = data.get("action")
        metadata = data.get("metadata") or {}
        if action in [UPLOAD_ACTION_ATTACHMENT] and not metadata.get("cipher_id"):
            raise serializers.ValidationError(detail={"metadata": {"cipher_id": ["This field is required"]}})

        return data


class SignedAttachmentSerializeR(serializers.Serializer):
    path = serializers.CharField(max_length=255)
