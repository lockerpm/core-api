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
    
    def to_internal_value(self, data):
        if "action" not in data:
            data["action"] = UPLOAD_ACTION_ATTACHMENT
        return super().to_internal_value(data)


class SignedAttachmentSerializer(serializers.Serializer):
    path = serializers.CharField(max_length=255)


class MultipleDeleteAttachmentSerializer(serializers.Serializer):
    paths = serializers.ListSerializer(
        child=serializers.CharField(max_length=512),
    )

    def validate(self, data):
        paths = data.get("paths")
        if len(paths) > 20:
            raise serializers.ValidationError(detail={"paths": ["You can only delete up to 20 paths at a time"]})
        return data
