from django.forms import model_to_dict
from rest_framework import serializers

from locker_server.shared.constants.transactions import LIST_DURATION, DURATION_MONTHLY, LIST_CURRENCY, CURRENCY_USD, \
    PLAN_TYPE_PM_ENTERPRISE, PLAN_TYPE_PM_ENTERPRISE_STARTUP


class ListInvoiceSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = {
            "id": instance.id,
            "payment_id": instance.payment_id,
            "created_time": instance.created_time,
            "total_price": instance.total_price,
            "discount": instance.discount,
            "status": instance.status,
            "payment_method": instance.payment_method,
            "duration": instance.status,
            "currency": instance.currency,
            "plan": instance.plan,
        }
        return data


class DetailInvoiceSerializer(ListInvoiceSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        customer = instance.customer
        promo_code = instance.promo_code

        data["customer"] = {
            "id": customer.customer_id,
            "full_name": customer.full_name,
            "organization": customer.organization,
            "address": customer.address,
            "city": customer.city,
            "state": customer.state,
            "postal_code": customer.postal_code,
            "last4": customer.last4,
            "brand": customer.brand,
            "country": {
                "country_code": customer.country.country_code,
                "country_name": customer.country.country_name,
                "country_phone_code": customer.country.country_phone_code,
            } if customer.country else None,

        } if customer is not None else None
        data["promo_code"] = promo_code.code if promo_code is not None else None

        return data


class CalcSerializer(serializers.Serializer):
    promo_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    duration = serializers.ChoiceField(choices=LIST_DURATION, default=DURATION_MONTHLY)
    currency = serializers.ChoiceField(choices=LIST_CURRENCY, default=CURRENCY_USD, required=False)


class CalcPublicSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(required=True, min_value=1)
    promo_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    duration = serializers.ChoiceField(choices=LIST_DURATION, default=DURATION_MONTHLY)
    currency = serializers.ChoiceField(choices=LIST_CURRENCY, default=CURRENCY_USD, required=False)


class UpgradePlanSerializer(serializers.Serializer):
    plan_alias = serializers.ChoiceField(
        choices=[PLAN_TYPE_PM_ENTERPRISE, PLAN_TYPE_PM_ENTERPRISE_STARTUP], default=PLAN_TYPE_PM_ENTERPRISE
    )
    promo_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    duration = serializers.ChoiceField(choices=LIST_DURATION, default=DURATION_MONTHLY, required=False)

    def validate(self, data):
        data["currency"] = CURRENCY_USD

        return data


class UpgradePlanPublicSerializer(UpgradePlanSerializer):
    plan_alias = serializers.ChoiceField(
        choices=[PLAN_TYPE_PM_ENTERPRISE, PLAN_TYPE_PM_ENTERPRISE_STARTUP], default=PLAN_TYPE_PM_ENTERPRISE
    )
    quantity = serializers.IntegerField(min_value=1, default=1)
    organization = serializers.CharField(max_length=128, default="My Enterprise")
    enterprise_address1 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    enterprise_address2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    enterprise_phone = serializers.CharField(max_length=128, required=False, allow_blank=True)
    enterprise_country = serializers.CharField(max_length=128, required=False, allow_blank=True)
    enterprise_postal_code = serializers.CharField(max_length=16, required=False, allow_blank=True)
    enterprise_registration_number = serializers.CharField(max_length=128, required=False, allow_blank=True)
    enterprise_registration_date = serializers.FloatField(required=False, allow_null=True)
    enterprise_entity_type = serializers.CharField(max_length=128, required=False, allow_blank=True)
    enterprise_vat_id = serializers.CharField(max_length=128, required=False, allow_blank=True)

    def validate(self, data):
        data = super().validate(data)
        plan_alias = data.get("plan_alias", PLAN_TYPE_PM_ENTERPRISE)
        if plan_alias == PLAN_TYPE_PM_ENTERPRISE_STARTUP:
            data["quantity"] = 1
        return data


class BillingAddressSerializer(serializers.Serializer):
    enterprise_name = serializers.CharField(max_length=128, required=False, allow_blank=True)
    enterprise_address1 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    enterprise_address2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    enterprise_postal_code = serializers.CharField(max_length=16, required=False, allow_blank=True)
    enterprise_country = serializers.CharField(max_length=128, required=False, allow_blank=True)
    enterprise_registration_number = serializers.CharField(max_length=128, required=False, allow_blank=True)
    enterprise_registration_date = serializers.FloatField(required=False, allow_null=True)
    enterprise_entity_type = serializers.CharField(max_length=128, required=False, allow_blank=True)
    enterprise_vat_id = serializers.CharField(max_length=128, required=False, allow_blank=True)
    enterprise_phone = serializers.CharField(max_length=128, required=False, allow_blank=True)

    def to_representation(self, instance):
        data = {
            "id": instance.enterprise_id,
            "enterprise_name": instance.enterprise_name,
            "enterprise_address1": instance.enterprise_address1,
            "enterprise_address2": instance.enterprise_address2,
            "enterprise_postal_code": instance.enterprise_postal_code,
            "enterprise_country": instance.enterprise_country,
            "enterprise_registration_number": instance.enterprise_registration_number,
            "enterprise_registration_date": instance.enterprise_registration_date,
            "enterprise_entity_type": instance.enterprise_entity_type,
            "enterprise_vat_id": instance.enterprise_vat_id,
            "enterprise_phone": instance.enterprise_phone,
        }
        return data
