from rest_framework import serializers

from locker_server.shared.constants.enterprise_members import ENTERPRISE_LIST_ROLE, E_MEMBER_ROLE_MEMBER, \
    E_MEMBER_STATUS_CONFIRMED, E_MEMBER_STATUS_INVITED


class DetailMemberSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {
            "id": instance.id,
            "access_time": instance.id,
            "'is_default'": instance.id,
            "is_primary": instance.id,
            "role": instance.id,
            "user_id": instance.id,
            "email": instance.id,
            "status": instance.id,
            "is_activated": instance.id,

        }
        data["role"] = instance.role.name
        data["pwd_user_id"] = instance.user.internal_id if instance.user else None
        data["domain"] = {
            "id": instance.domain_id,
            "domain": instance.domain.domain
        } if instance.domain else None
        if hasattr(instance, "group_members"):
            group_members = instance.group_members
            group_names = [group_member.group.name for group_member in group_members]
            data["groups"] = group_names
        if instance.status != E_MEMBER_STATUS_INVITED:
            data["security_score"] = instance.user.master_password_score if instance.user else None
        else:
            data["security_score"] = None
            data["access_time"] = None
        return data


class CreateMemberSerializer(serializers.Serializer):
    is_default = serializers.BooleanField()
    role = serializers.ChoiceField(choices=ENTERPRISE_LIST_ROLE)
    user_id = serializers.CharField()


class ShortDetailMemberSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {
            "id": instance.id,
            "role": instance.id,
            "user_id": instance.id,
            "email": instance.id,
            "status": instance.id,

        }
        return data


class DetailActiveMemberSerializer(DetailMemberSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["login_block_until"] = instance.user.login_block_until if instance.user else None
        data["cipher_overview"] = instance.cipher_overview
        return data


class UpdateMemberSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=ENTERPRISE_LIST_ROLE, default=E_MEMBER_ROLE_MEMBER, required=False
    )
    status = serializers.ChoiceField(choices=[E_MEMBER_STATUS_CONFIRMED], required=False)

    def validate(self, data):
        role = data.get("role")
        status = data.get("status")
        if status is None and role is None:
            raise serializers.ValidationError(detail={"role": ["The role or status is required"]})
        return data


class EnabledMemberSerializer(serializers.Serializer):
    activated = serializers.BooleanField()


class UserInvitationSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {
            "id": instance.enterprise_member_id,
            "access_time": instance.access_time,
            "role": instance.role.name,
            "status": instance.status
        }
        data["enterprise"] = {
            "id": instance.enterprise.enterprise_id,
            "name": instance.enterprise.name
        }
        data["owner"] = instance.enterprise.enterprise_members.get(is_primary=True).user_id
        if instance.domain is not None:
            data["domain"] = {
                "id": instance.domain.domain_id,
                "domain": instance.domain.domain,
                "auto_approve": instance.domain.auto_approve
            }
        else:
            data["domain"] = None
        return data


class UpdateUserInvitationSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["confirmed", "reject"])


class SearchMemberGroupSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=255)
    user_ids = serializers.ListSerializer(
        child=serializers.IntegerField(), allow_null=True, allow_empty=True, required=False
    )


class EnterpriseGroupSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {
            "id": instance.enterprise_group_id,
            "name": instance.name,
            "creation_date": instance.creation_date,
            "revision_date": instance.revision_date,
        }
        return data