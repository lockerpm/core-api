from rest_framework import serializers


class ListEnterpriseGroupSerializer(serializers.Serializer):
    def to_representation(self, instance):
        count_group_members_func = self.context.get("count_group_members_func")
        if callable(count_group_members_func):
            number_members = count_group_members_func(instance.enterprise_group_id)
        else:
            number_members = 1
        data = {
            "id": instance.enterprise_group_id,
            "name": instance.name,
            "creation_date": instance.creation_date,
            "revision_date": instance.revision_date,
            "number_members": number_members
        }
        created_by = instance.created_by
        if created_by:
            data["created_by"] = {
                "email": created_by.email,
                "username": created_by.username,
                "full_name": created_by.full_name,
                "avatar": created_by.get_avatar()
            }
        return data


class ShortDetailEnterpriseGroupSerializer(ListEnterpriseGroupSerializer):
    def to_representation(self, instance):
        return super().to_representation(instance)


class UpdateEnterpriseGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)


class CreateEnterpriseGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)


class UpdateMemberGroupSerializer(serializers.Serializer):
    members = serializers.ListField(child=serializers.CharField(), allow_empty=True)
