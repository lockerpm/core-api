from rest_framework import serializers


class UpdateAppInfoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, allow_blank=False, allow_null=False)


class UpdateAppLogoSerializer(serializers.Serializer):
    logo = serializers.ImageField()
