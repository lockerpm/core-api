from rest_framework import serializers

from locker_server.shared.constants.release import *
from locker_server.shared.constants.device_type import *


class NewReleaseSerializer(serializers.Serializer):
    build = serializers.BooleanField()
    client_id = serializers.ChoiceField(
        choices=[CLIENT_ID_BROWSER, CLIENT_ID_DESKTOP, CLIENT_ID_DESKTOP_SERVICE, CLIENT_ID_CLI,
                 CLIENT_ID_SDK_PYTHON, CLIENT_ID_SDK_NODEJS, CLIENT_ID_SDK_DOTNET],
        default=CLIENT_ID_DESKTOP
    )
    environment = serializers.ChoiceField(choices=LIST_RELEASE_ENVIRONMENT, default=RELEASE_ENVIRONMENT_PROD)
    checksum = serializers.DictField(required=False, allow_null=True)
    platform = serializers.ChoiceField(choices=LIST_RELEASE_PLATFORM, allow_null=True, default=None, required=False)


class NextReleaseSerializer(serializers.Serializer):
    client_id = serializers.ChoiceField(
        choices=[CLIENT_ID_BROWSER, CLIENT_ID_DESKTOP, CLIENT_ID_DESKTOP_SERVICE, CLIENT_ID_CLI,
                 CLIENT_ID_SDK_PYTHON, CLIENT_ID_SDK_NODEJS, CLIENT_ID_SDK_DOTNET],
        default=CLIENT_ID_DESKTOP
    )
    environment = serializers.ChoiceField(choices=LIST_RELEASE_ENVIRONMENT, default=RELEASE_ENVIRONMENT_PROD)
    platform = serializers.ChoiceField(choices=LIST_RELEASE_PLATFORM, allow_null=True, default=None, required=False)


class ListReleaseSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {
            "version": instance.version,
            "environment": instance.environment,
            "platform": instance.platform,
            "checksum": instance.get_checksum()
        }
        return data


class DetailReleaseSerializer(ListReleaseSerializer):
    def to_representation(self, instance):
        return super().to_representation(instance=instance)
