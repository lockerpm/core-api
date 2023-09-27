import json

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.micro_service_permissions.mobile_permission import MobilePaymentPermission
from locker_server.api.permissions.micro_service_permissions.user_permission import UserPermission
from locker_server.core.exceptions.user_exception import UserDoesNotExistException
from locker_server.shared.constants.device_type import CLIENT_ID_MOBILE
from locker_server.shared.constants.transactions import *
from locker_server.shared.utils.app import now
from .serializers import UpgradePlanSerializer, MobileRenewalSerializer, MobileCancelSubscriptionSerializer, \
    MobileDestroySubscriptionSerializer


class MobilePaymentViewSet(APIBaseViewSet):
    permission_classes = (MobilePaymentPermission, )
    http_method_names = ["head", "options", "post", "put"]

    def get_serializer_class(self):
        if self.action == "upgrade_plan":
            self.serializer_class = UpgradePlanSerializer
        elif self.action == "mobile_renewal":
            self.serializer_class = MobileRenewalSerializer
        elif self.action == "mobile_cancel_subscription":
            self.serializer_class = MobileCancelSubscriptionSerializer
        elif self.action == "mobile_destroy_subscription":
            self.serializer_class = MobileDestroySubscriptionSerializer
        return super().get_serializer_class()

    @action(methods=["post"], detail=False)
    def upgrade_plan(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user_id = validated_data.get("user_id")
        family_members = json.loads(json.dumps(validated_data.get("family_members", [])))
        description = validated_data.get("description", "")
        promo_code = validated_data.get("promo_code")
        paid = validated_data.get("paid", True)
        duration = validated_data.get("duration", DURATION_MONTHLY)
        plan = validated_data.get("plan")
        platform = validated_data.get("platform")
        mobile_invoice_id = validated_data.get("mobile_invoice_id")
        mobile_original_id = validated_data.get("mobile_original_id")
        confirm_original_id = validated_data.get("confirm_original_id")
        currency = validated_data.get("currency", CURRENCY_USD)
        failure_reason = validated_data.get("failure_reason")
        is_trial_period = validated_data.get("is_trial_period", False)

        try:
            new_payment = self.mobile_payment_service.upgrade_plan(
                user_id=user_id, plan_alias=plan, duration=duration,
                promo_code=promo_code, paid=paid, failure_reason=failure_reason,
                is_trial_period=is_trial_period,
                payment_platform="iOS" if "ios" in request.path else "Android",
                scope=settings.SCOPE_PWD_MANAGER,
                **{
                    "description": description,
                    "failure_reason"
                    "family_members": family_members,
                    "platform": platform,
                    "mobile_invoice_id": mobile_invoice_id,
                    "mobile_original_id": mobile_original_id,
                    "confirm_original_id": confirm_original_id,
                    "currency": currency,
                }
            )
        except UserDoesNotExistException:
            raise ValidationError(detail={"user_id": ["User does not exist"]})

        return Response(status=status.HTTP_200_OK, data={
            "success": True,
            "scope": new_payment.scope,
            "payment_id": new_payment.payment_id
        })

    @action(methods=["post"], detail=False)
    def mobile_renewal(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            pass
        except UserDoesNotExistException:
            raise ValidationError(detail={
                "mobile_original_id": ["The mobile subscription id does not exist"]
            })

        user = validated_data.get("user")
        description = validated_data.get("description", "")
        promo_code = validated_data.get("promo_code")
        status = validated_data.get("status", True)
        duration = validated_data.get("duration", DURATION_MONTHLY)
        plan = validated_data.get("plan")
        platform = validated_data.get("platform")
        mobile_invoice_id = validated_data.get("mobile_invoice_id")
        mobile_original_id = validated_data.get("mobile_original_id")
        currency = validated_data.get("currency", CURRENCY_USD)
        failure_reason = validated_data.get("failure_reason")
        end_period = validated_data.get("end_period")

        # Check the invoice with mobile_invoice_id exists or not?
        mobile_invoice_exist = False
        if mobile_invoice_id:
            mobile_invoice_exist = Payment.objects.filter(mobile_invoice_id=mobile_invoice_id).exists()

        # If we don't have any payment with mobile_invoice_id => Create new one
        if mobile_invoice_exist is False:
            new_payment_data = {
                "user": user,
                "description": description,
                "plan": plan,
                "duration": duration,
                "promo_code": promo_code,
                "currency": currency,
                "payment_method": PAYMENT_METHOD_MOBILE,
                "mobile_invoice_id": mobile_invoice_id,
                "metadata": {
                    "platform": platform,
                    "mobile_invoice_id": mobile_invoice_id,
                    "mobile_original_id": mobile_original_id,
                    "user_id": user.user_id,
                    "scope": settings.SCOPE_PWD_MANAGER,
                    "key": validated_data.get("key"),
                    "collection_name": validated_data.get("collection_name")
                }
            }
            # Create new payment
            new_payment = Payment.create(**new_payment_data)
        # Else, retrieving the payment with mobile_invoice_id
        else:
            new_payment = Payment.objects.filter(mobile_invoice_id=mobile_invoice_id).first()

        # Set paid or not
        if status == PAYMENT_STATUS_PAID:
            # If this plan is canceled because the Personal Plan upgrade to Enterprise Plan => Not downgrade
            current_plan = self.user_repository.get_current_plan(user=user, scope=settings.SCOPE_PWD_MANAGER)
            if current_plan.is_update_personal_to_enterprise(new_plan_alias=new_payment.plan) is True:
                return Response(status=200, data={"is_update_personal_to_enterprise": True})

            # Upgrade new plan
            subscription_metadata = {
                "end_period": end_period,
                "promo_code": new_payment.promo_code,
                "key": validated_data.get("key"),
                "collection_name": validated_data.get("collection_name")
            }
            self.user_repository.update_plan(
                new_payment.user, plan_type_alias=new_payment.plan, duration=new_payment.duration,
                scope=settings.SCOPE_PWD_MANAGER,
                **subscription_metadata
            )
            # Set default payment method
            try:
                current_plan = self.user_repository.get_current_plan(user=user, scope=settings.SCOPE_PWD_MANAGER)
                current_plan.set_default_payment_method(PAYMENT_METHOD_MOBILE)
            except ObjectDoesNotExist:
                pass

            if new_payment.status != PAYMENT_STATUS_PAID:
                self.payment_repository.set_paid(payment=new_payment)
                # Send mail
                LockerBackgroundFactory.get_background(bg_name=BG_NOTIFY, background=False).run(
                    func_name="pay_successfully", **{"payment": new_payment, "payment_platform": platform.title()}
                )
        elif status == PAYMENT_STATUS_PAST_DUE:
            self.payment_repository.set_past_due(payment=new_payment, failure_reason=failure_reason)
        else:
            self.payment_repository.set_failed(payment=new_payment, failure_reason=failure_reason)
            # Only Downgrade - Not set mobile_original_id is Null
            current_plan = self.user_repository.get_current_plan(user=user, scope=settings.SCOPE_PWD_MANAGER)
            if current_plan.is_update_personal_to_enterprise(new_plan_alias=new_payment.plan) is True:
                return Response(status=200, data={"is_update_personal_to_enterprise": True})

            old_plan = current_plan.get_plan_type_name()
            if not current_plan.user.pm_plan_family.exists():
                self.user_repository.update_plan(
                    user=user, plan_type_alias=PLAN_TYPE_PM_FREE, scope=settings.SCOPE_PWD_MANAGER
                )
                # Notify downgrade here
                LockerBackgroundFactory.get_background(bg_name=BG_NOTIFY, background=True).run(
                    func_name="downgrade_plan", **{
                        "user_id": user.user_id, "old_plan": old_plan, "downgrade_time": now(),
                        "scope": settings.SCOPE_PWD_MANAGER, **{"payment_data": {}}
                    }
                )

        return Response(status=200, data={
            "success": True,
            "user_id": user.user_id,
            "scope": new_payment.scope,
            "status": new_payment.status,
            "failure_reason": failure_reason,
            "payment_id": new_payment.payment_id
        })