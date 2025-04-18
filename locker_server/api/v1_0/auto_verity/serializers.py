from rest_framework import serializers


class CreateAutoVerifySerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=64)
    h = serializers.CharField(max_length=128)
    p = serializers.CharField(max_length=128)


class DeviceAutoVerifySerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=64)
    ts = serializers.IntegerField()
    s = serializers.CharField(max_length=128)
    pk = serializers.CharField(max_length=1024)


class DeleteDeviceAutoVerifySerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=64)
