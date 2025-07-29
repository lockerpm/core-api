from rest_framework import serializers

from locker_server.core.entities.scam_setting.scam_setting import ScamSetting
from locker_server.core.entities.scam_setting.whitelist_scam_url import WhitelistScamUrl
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


class DetailWlScamUrlSerializer(serializers.Serializer):
    def to_representation(self, instance: WhitelistScamUrl):
        return {
            "id": instance.whitelist_scam_url_id,
            "url": instance.url,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }


class ListWlScamUrlSerializer(DetailWlScamUrlSerializer):
    def to_representation(self, instance: WhitelistScamUrl):
        return super().to_representation(instance)


class UpdateWlScamUrlSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=512)


class CreateWlScamUrlSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=512)
