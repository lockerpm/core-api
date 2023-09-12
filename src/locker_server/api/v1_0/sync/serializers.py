from rest_framework import serializers

from locker_server.shared.constants.members import MEMBER_ROLE_MEMBER
from locker_server.shared.utils.app import convert_readable_date


class SyncFolderSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = {
            "object": "folder",
            "id": instance.folder_id,
            "name": instance.name,
            "revision_date": convert_readable_date(instance.revision_date),
            "creation_date": convert_readable_date(instance.creation_date),
        }
        return data


class SyncCollectionSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = {
            "object": "collectionDetails",
            "id": instance.collection_id,
            "name": instance.name,
            "revision_date": convert_readable_date(instance.revision_date),
            "organization_id": instance.team.team_id,
            "hide_passwords": instance.hide_passwords,
            "external_id": None,
        }
        return data


class SyncEnterprisePolicySerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = {
            "object": "policyDetails",
            "enterprise_id": instance.enterprise.enterprise_id,
            "enabled": instance.enabled,
            "policy_type": instance.policy_type,
            "config": instance.config
        }
        return data
