from rest_framework import serializers


class ListEnterpriseGroupSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {
            "id": instance.enterprise_group_id,
            "name": instance.name,
            "creation_date": instance.creation_date,
            "revision_date": instance.revision_date,
            "created_by": instance.created_by.user_id,
            "number_members": len(instance.group_members)
        }
        return data


class ShortDetailEnterpriseGroupSerializer(ListEnterpriseGroupSerializer):
    def to_representation(self, instance):
        return super().to_representation(instance)


class UpdateEnterpriseGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)


class CreateEnterpriseGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)


class DetailEnterpriseGroupSerializer(ShortDetailEnterpriseGroupSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        enterprise_members = []
        group_members = instance.group_members
        for group_member in group_members:
            enterprise_members.append(
                group_member.member
            )
        data["members"] = [{
            "user_id": enterprise_member.user.user_id,
            "email": enterprise_member.email,
            "status": enterprise_member.status,
            "role": enterprise_member.role.name,
            "domain_id": enterprise_member.domain_id,
            "is_activated": enterprise_member.is_activated,
            "public_key": enterprise_member.user.public_key if enterprise_member.user else None
        } for enterprise_member in enterprise_members]
        return data


class UpdateMemberGroupSerializer(serializers.Serializer):
    members = serializers.ListField(child=serializers.CharField(), allow_empty=True)
