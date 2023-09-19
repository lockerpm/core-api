from rest_framework import serializers


class FamilyMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(allow_null=True)
    email = serializers.EmailField()
