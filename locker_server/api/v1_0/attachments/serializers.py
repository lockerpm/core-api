from rest_framework import serializers

from locker_server.shared.constants.attachments import UPLOAD_ACTION_ATTACHMENT


class AttachmentUploadSerializer(serializers.Serializer):
    file_name = serializers.CharField(max_length=255)
    action = serializers.ChoiceField(
        choices=[UPLOAD_ACTION_ATTACHMENT],
        default=UPLOAD_ACTION_ATTACHMENT
    )
    # metadata = AttachmentUploadMetadataSerializer(many=False, required=False)

    def validate(self, data):
        # action = data.get("action")
        # metadata = data.get("metadata") or {}
        # if action in [UPLOAD_ACTION_MESSAGE_GROUP, UPLOAD_ACTION_AVATAR_GROUP] and not metadata.get("group_chat_id"):
        #     raise serializers.ValidationError(detail={"metadata": {"group_chat_id": ["This field is required"]}})
        #
        # if action in [UPLOAD_ACTION_LINK_DEVICE, UPLOAD_ACTION_FEEDBACK, UPLOAD_ACTION_AVATAR_USER]:
        #     metadata.update({"username": self.context["request"].auth.user.username})
        #     data["metadata"] = metadata
        #
        # if action not in [UPLOAD_ACTION_MESSAGE_GROUP, UPLOAD_ACTION_MESSAGE]:
        #     data["thumb_file_name"] = None

        return data


class SignedAttachmentSerializeR(serializers.Serializer):
    path = serializers.CharField(max_length=255)
