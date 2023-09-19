from rest_framework import serializers

from locker_server.shared.constants.release import LIST_RELEASE_ENVIRONMENT, RELEASE_ENVIRONMENT_PROD
from locker_server.shared.constants.device_type import CLIENT_ID_BROWSER, CLIENT_ID_DESKTOP


class NewReleaseSerializer(serializers.Serializer):
    build = serializers.BooleanField()
    client_id = serializers.ChoiceField(choices=[CLIENT_ID_BROWSER, CLIENT_ID_DESKTOP], default=CLIENT_ID_DESKTOP)
    environment = serializers.ChoiceField(choices=LIST_RELEASE_ENVIRONMENT, default=RELEASE_ENVIRONMENT_PROD)


class NextReleaseSerializer(serializers.Serializer):
    client_id = serializers.ChoiceField(choices=[CLIENT_ID_BROWSER, CLIENT_ID_DESKTOP], default=CLIENT_ID_DESKTOP)
    environment = serializers.ChoiceField(choices=LIST_RELEASE_ENVIRONMENT, default=RELEASE_ENVIRONMENT_PROD)
