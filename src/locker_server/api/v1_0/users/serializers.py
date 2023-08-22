from rest_framework import serializers

from locker_server.shared.constants.account import LOGIN_METHOD_PASSWORD, LOGIN_METHOD_PASSWORDLESS
from locker_server.shared.constants.ciphers import KDF_TYPE
from locker_server.shared.constants.device_type import LIST_CLIENT_ID, LIST_DEVICE_TYPE
from locker_server.shared.constants.transactions import *


class UserMeSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {
            "timeout": instance.timeout,
            "timeout_action": instance.timeout_action,
            "is_pwd_manager": instance.activated,
            "pwd_user_id": str(instance.user_id),
        }
        show_key_param = self.context["request"].query_params.get("show_key", "0")
        if show_key_param == "1":
            data.update({
                "key": instance.key,
                "public_key": instance.public_key,
                "private_key": instance.private_key
            })
        return data


class UserScoreUpdateSerializer(serializers.Serializer):
    cipher0 = serializers.IntegerField(min_value=0, required=False)
    cipher1 = serializers.IntegerField(min_value=0, required=False)
    cipher2 = serializers.IntegerField(min_value=0, required=False)
    cipher3 = serializers.IntegerField(min_value=0, required=False)
    cipher4 = serializers.IntegerField(min_value=0, required=False)
    cipher5 = serializers.IntegerField(min_value=0, required=False)
    cipher6 = serializers.IntegerField(min_value=0, required=False)
    cipher7 = serializers.IntegerField(min_value=0, required=False)


class UserUpdateMeSerializer(serializers.Serializer):
    timeout = serializers.IntegerField(allow_null=True, min_value=0, required=False)
    timeout_action = serializers.ChoiceField(choices=["lock", "logOut"], required=False)
    scores = UserScoreUpdateSerializer(allow_null=True, required=False, many=False)


class EncryptedPairKey(serializers.Serializer):
    encrypted_private_key = serializers.CharField()
    public_key = serializers.CharField()


class UserRegisterSerializer(serializers.Serializer):
    kdf = serializers.IntegerField(default=0)
    kdf_iterations = serializers.IntegerField(default=100000)
    key = serializers.CharField()
    keys = EncryptedPairKey(many=False)
    master_password_hash = serializers.CharField(allow_blank=False)
    master_password_hint = serializers.CharField(allow_blank=True, max_length=128)
    score = serializers.FloatField(required=False, allow_null=True)
    trial_plan = serializers.ChoiceField(
        choices=[PLAN_TYPE_PM_FREE, PLAN_TYPE_PM_PREMIUM, PLAN_TYPE_PM_FAMILY, PLAN_TYPE_PM_ENTERPRISE],
        required=False, allow_null=True
    )
    is_trial_promotion = serializers.BooleanField(default=False, allow_null=True, required=False)
    enterprise_name = serializers.CharField(required=False, allow_null=True)

    def validate(self, data):
        kdf_type = data.get("kdf_type", 0)
        if not KDF_TYPE.get(kdf_type):
            raise serializers.ValidationError(detail={"kdf": ["This KDF Type is not valid"]})
        kdf_iterations = data.get("kdf_iterations", 100000)
        if kdf_iterations < 5000 or kdf_iterations > 1000000:
            raise serializers.ValidationError(detail={
                "kdf_iterations": ["KDF iterations must be between 5000 and 1000000"]
            })

        return data


class UserSessionSerializer(serializers.Serializer):
    client_id = serializers.ChoiceField(choices=LIST_CLIENT_ID)
    device_identifier = serializers.CharField()
    device_name = serializers.CharField(required=False, allow_blank=True)
    device_type = serializers.IntegerField(required=False)
    password = serializers.CharField()

    def validate(self, data):
        device_type = data.get("device_type")
        if device_type and device_type not in LIST_DEVICE_TYPE:
            raise serializers.ValidationError(detail={"device_type": ["The device type is not valid"]})
        return data


class DeviceFcmSerializer(serializers.Serializer):
    fcm_id = serializers.CharField(max_length=255, allow_null=True)
    device_identifier = serializers.CharField(max_length=128)


class UserChangePasswordSerializer(serializers.Serializer):
    key = serializers.CharField()
    master_password_hash = serializers.CharField()
    new_master_password_hash = serializers.CharField()
    new_master_password_hint = serializers.CharField(allow_blank=True, max_length=128, required=False)
    score = serializers.FloatField(required=False, allow_null=True)
    login_method = serializers.ChoiceField(choices=[LOGIN_METHOD_PASSWORD, LOGIN_METHOD_PASSWORDLESS], required=False)


class UserNewPasswordSerializer(serializers.Serializer):
    key = serializers.CharField()
    new_master_password_hash = serializers.CharField()
    new_master_password_hint = serializers.CharField(allow_blank=True, max_length=128, required=False)
    score = serializers.FloatField(required=False, allow_null=True)
    login_method = serializers.ChoiceField(choices=[LOGIN_METHOD_PASSWORD, LOGIN_METHOD_PASSWORDLESS])
