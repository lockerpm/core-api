from rest_framework import serializers

from locker_server.core.entities.scam_setting.scam_setting import ScamSetting
from locker_server.shared.constants.scam_setting import LIST_SCAM_SETTING_CATEGORIES


class ScamSettingSerializer(serializers.Serializer):

    def to_representation(self, instance: ScamSetting):
        category = instance.category
        data = {
            "enabled": instance.enabled,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
            "category": {
                "id": category.scam_setting_category_id,
                "name": category.name,
                "name_vi": category.name_vi,
            }
        }
        return data


class UpdateScamSettingSerializer(serializers.Serializer):
    category_id = serializers.ChoiceField(choices=LIST_SCAM_SETTING_CATEGORIES)
    enabled = serializers.BooleanField()
