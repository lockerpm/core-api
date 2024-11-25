from rest_framework import serializers


class CountrySerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {
            "country_code": instance.country_code,
            "country_name": instance.country_name,
            "country_phone_code": instance.country_phone_code,
        }
        return data


class IndividualPlanSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {
            "id": instance.plan_id,
            "name": instance.name,
            "alias": instance.alias,
        }
        return data


class AutofillKeySerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {
            "key": instance.key,
            "values": instance.values
        }
        return data
