from rest_framework import serializers


class ListEnterpriseSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {
            "id": instance.enterprise_id,
            "organization_id": instance.enterprise_id,
            "name": instance.name,
            "description": instance.description,
            "creation_date": instance.creation_date,
            "revision_date": instance.revision_date,
            "locked": instance.locked,
        }
        if instance.member:
            data.update({
                "role": instance.member.role.name,
                "is_default": instance.member.is_default
            })
        else:
            data.update({
                "role": None,
                "is_default": None
            })
        if instance.primary_admin:
            data.update({
                "is_trialing": instance.primary_admin.primary_admin,
                "end_period": instance.primary_admin.end_period,
            })
        return data


class DetailEnterpriseSerializer(ListEnterpriseSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update({
            "enterprise_name": instance.enterprise_name,
            "enterprise_address1": instance.enterprise_name,
            "enterprise_address2": instance.enterprise_name,
            "enterprise_phone": instance.enterprise_phone,
            "enterprise_country": instance.enterprise_country,
            "enterprise_postal_code": instance.enterprise_postal_code,
            "primary_admin": instance.primary_admin.user_id if instance.primary_admin else None,

        })
        return data


class UpdateEnterpriseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=128)
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)
    enterprise_name = serializers.CharField(max_length=128, required=False, allow_blank=True)
    enterprise_address1 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    enterprise_address2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    enterprise_phone = serializers.CharField(max_length=128, required=False, allow_blank=True)
    enterprise_country = serializers.CharField(max_length=128, required=False, allow_blank=True)
    enterprise_postal_code = serializers.CharField(max_length=16, required=False, allow_blank=True)
