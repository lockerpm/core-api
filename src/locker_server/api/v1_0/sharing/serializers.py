from rest_framework import serializers


class UserPublicKeySerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class SharingInvitationSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {
            "id": instance.team_member_id,
            "access_time": instance.access_time,
            "role": instance.role.name,
            "status": instance.status,
            "team": {
                "id": instance.team.team_id,
                "organization_id": instance.team.team_id,
                "name": instance.team.name,
            },
            "hide_passwords": instance.hide_passwords,
        }
        return data
