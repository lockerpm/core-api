from rest_framework import serializers

from locker_server.shared.constants.sso_provider import LIST_OIDC_BEHAVIOR, OIDC_BEHAVIOR_POST, \
    LIST_VALID_SSO_PROVIDERS, \
    SSO_PROVIDER_OIDC, SSO_PROVIDER_SAML


class ListSSOConfigurationSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {
            "id": instance.sso_configuration_id,
            "identifier": instance.identifier,
            "enabled": instance.enabled,
            "sso_provider": instance.sso_provider.sso_provider_id,
            "sso_provider_options": instance.sso_provider_options,
            "creation_date": instance.creation_date,
            "revision_date": instance.revision_date
        }
        if instance.created_by:
            data.update({
                "created_by": {
                    "id": instance.created_by.user_id,
                    "username": instance.created_by.username
                }
            })
        return data


class DetailSSOConfigurationSerializer(ListSSOConfigurationSerializer):
    def to_representation(self, instance):
        return super().to_representation(instance=instance)


class OIDCOptionSerializer(serializers.Serializer):
    client_id = serializers.CharField(required=True)
    client_secret = serializers.CharField(required=True)
    authority = serializers.CharField(required=True)
    redirect_behavior = serializers.ChoiceField(choices=LIST_OIDC_BEHAVIOR, default=OIDC_BEHAVIOR_POST)
    userinfo_endpoint = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    scopes = serializers.CharField(required=False, default="openid")
    user_id_claim_types = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    email_claim_types = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    name_claim_types = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class SAMLOptionSerializer(serializers.Serializer):
    idp_entity_id = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    idp_single_sign_on_service_url = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    idp_single_log_out_service_url = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    idp_x509_public_cert = serializers.CharField(required=True)


class UpdateSSOConfigurationSerializer(serializers.Serializer):
    sso_provider = serializers.ChoiceField(choices=LIST_VALID_SSO_PROVIDERS, required=False)
    identifier = serializers.CharField(max_length=255, required=False, allow_blank=False)
    enabled = serializers.BooleanField(required=False, default=False)
    sso_provider_options = serializers.DictField(required=False, allow_null=True)

    def validate(self, data):
        sso_provider = data.get("sso_provider")
        sso_provider_options = data.get("sso_provider_options")
        if sso_provider:
            option_srl = None
            option_is_valid = None
            if sso_provider == SSO_PROVIDER_OIDC:
                option_srl = OIDCOptionSerializer(data=sso_provider_options)
            elif sso_provider == SSO_PROVIDER_SAML:
                option_srl = SAMLOptionSerializer(data=sso_provider_options)
            if option_srl:
                option_is_valid = option_srl.is_valid(raise_exception=False)
            if option_is_valid is not None and option_is_valid is False:
                # option_srl.errors
                raise serializers.ValidationError(detail={"sso_provider_options": option_srl.errors})
            data["sso_provider_options"] = option_srl.validated_data
        return data


class CreateSSOConfigurationSerializer(UpdateSSOConfigurationSerializer):
    sso_provider = serializers.ChoiceField(choices=LIST_VALID_SSO_PROVIDERS, required=True)
    identifier = serializers.CharField(max_length=255, required=True, allow_blank=False)
    enabled = serializers.BooleanField(required=False, default=False)
    sso_provider_options = serializers.DictField(required=False, allow_null=True)

    def validate(self, data):
        sso_provider = data.get("sso_provider")
        sso_provider_options = data.get("sso_provider_options")
        option_srl = None
        option_is_valid = None
        if sso_provider == SSO_PROVIDER_OIDC:
            option_srl = OIDCOptionSerializer(data=sso_provider_options)
        elif sso_provider == SSO_PROVIDER_SAML:
            option_srl = SAMLOptionSerializer(data=sso_provider_options)
        if option_srl:
            option_is_valid = option_srl.is_valid(raise_exception=False)
        if option_is_valid is not None and option_is_valid is False:
            # option_srl.errors
            raise serializers.ValidationError(detail={"sso_provider_options": option_srl.errors})
        data["sso_provider_options"] = option_srl.validated_data
        return data


class RetrieveUserSerializer(serializers.Serializer):
    sso_identifier = serializers.CharField(max_length=255, required=True, allow_blank=False)
    auth_token = serializers.CharField(required=True, allow_blank=False)
