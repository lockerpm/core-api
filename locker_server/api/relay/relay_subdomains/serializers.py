from rest_framework import serializers


class ListRelaySubdomainsSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {
            "id": instance.relay_subdomain_id,
            "subdomain": instance.subdomain,
            "created_time": instance.created_time,
            "num_alias": instance.num_alias,
            "num_spam": instance.num_spam,
            "num_forwarded": instance.num_forwarded,
        }
        return data


class DetailRelaySubdomainSerializer(ListRelaySubdomainsSerializer):
    def to_representation(self, instance):
        return super().to_representation(instance)


class CreateRelaySubdomainSerializer(serializers.Serializer):
    subdomain = serializers.CharField(max_length=64, min_length=3)

    def validate(self, data):
        subdomain = data.get("subdomain").strip()
        data["subdomain"] = subdomain
        return data


class UpdateRelaySubdomainSerializer(CreateRelaySubdomainSerializer):
    """"""


class UseRelaySubdomainSerializer(serializers.Serializer):
    use_relay_subdomain = serializers.BooleanField()
