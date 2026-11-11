from contextlib import nullcontext
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings

from locker_server.api.v1_0.payments.serializers import CalcLifetimePublicSerializer, \
    UpgradeLifetimePublicSerializer, UpgradePlanSerializer, UpgradeSubscriptionPublicSerializer
from locker_server.api_orm.repositories import user_plan_repository as user_plan_repository_module
from locker_server.api_orm.repositories.user_plan_repository import UserPlanORMRepository
from locker_server.core.entities.user_plan.pm_plan import PMPlan
from locker_server.core.exceptions.payment_exception import MaxFamilyMemberReachedException
from locker_server.core.exceptions.user_plan_exception import MaxUserPlanFamilyReachedException
from locker_server.core.services.payment_hook_service import PaymentHookService
from locker_server.core.services.payment_service import PaymentService
from locker_server.shared.constants.transactions import LIST_FAMILY_PLAN, LIST_LIFETIME_FAMILY_PLAN, \
    LIST_LIFETIME_PLAN, PLAN_TYPE_PM_LIFETIME_COUPLE, PLAN_TYPE_PM_PREMIUM


def build_couple_plan() -> PMPlan:
    return PMPlan(
        plan_id=12, alias=PLAN_TYPE_PM_LIFETIME_COUPLE, name="Lifetime Couple",
        price_usd=0, price_vnd=0, half_yearly_price_usd=0, half_yearly_price_vnd=0,
        yearly_price_usd=0, yearly_price_vnd=0,
        is_family_plan=True, is_team_plan=False, max_number=2,
    )


class LifetimeCouplePlanConstantsTestCase(SimpleTestCase):
    def test_couple_is_a_lifetime_family_plan(self):
        self.assertEqual(PLAN_TYPE_PM_LIFETIME_COUPLE, "pm_lifetime_couple")
        self.assertIn(PLAN_TYPE_PM_LIFETIME_COUPLE, LIST_LIFETIME_PLAN)
        self.assertIn(PLAN_TYPE_PM_LIFETIME_COUPLE, LIST_FAMILY_PLAN)
        self.assertIn(PLAN_TYPE_PM_LIFETIME_COUPLE, LIST_LIFETIME_FAMILY_PLAN)


class LifetimeCoupleNotSoldByStripeTestCase(SimpleTestCase):
    def test_stripe_serializers_reject_couple_plan(self):
        serializer_classes = [
            CalcLifetimePublicSerializer, UpgradeLifetimePublicSerializer,
            UpgradePlanSerializer, UpgradeSubscriptionPublicSerializer,
        ]
        for serializer_class in serializer_classes:
            with self.subTest(serializer=serializer_class.__name__):
                serializer = serializer_class(data={"plan_alias": PLAN_TYPE_PM_LIFETIME_COUPLE})
                self.assertFalse(serializer.is_valid())
                self.assertIn("plan_alias", serializer.errors)


class UpgradeLifetimeCoupleByCodeTestCase(SimpleTestCase):
    def setUp(self):
        self.payment_repository = MagicMock()
        self.user_plan_repository = MagicMock()
        self.plan_repository = MagicMock()
        self.user_repository = MagicMock()
        self.enterprise_member_repository = MagicMock()
        self.service = PaymentService(
            payment_repository=self.payment_repository,
            user_plan_repository=self.user_plan_repository,
            plan_repository=self.plan_repository,
            user_repository=self.user_repository,
            enterprise_member_repository=self.enterprise_member_repository,
            education_email_repository=MagicMock(),
            cipher_repository=MagicMock(),
            relay_address_repository=MagicMock(),
            attachment_storage=MagicMock(),
        )

        self.enterprise_member_repository.is_in_enterprise.return_value = False
        saas_code = MagicMock()
        saas_code.saas_plan = PLAN_TYPE_PM_LIFETIME_COUPLE
        saas_code.remaining_times = 0
        saas_code.saas_market.lifetime_duration = None
        self.payment_repository.check_saas_promo_code.return_value = saas_code
        self.payment_repository.update_promo_code_remaining_times.return_value = saas_code
        self.plan_repository.get_plan_by_alias.return_value = build_couple_plan()
        current_plan = MagicMock()
        current_plan.pm_stripe_subscription = None
        self.user_plan_repository.get_user_plan.return_value = current_plan
        self.user_plan_repository.is_family_member.return_value = False
        self.user_repository.update_user.return_value = MagicMock(activated=False)

    def test_upgrade_to_couple_plan_by_code(self):
        self.user_plan_repository.count_family_members.return_value = 1

        self.service.upgrade_lifetime(user_id=1, code="COUPLE-CODE")

        self.payment_repository.update_promo_code_remaining_times.assert_called_once()
        self.user_plan_repository.update_plan.assert_called_once()
        update_kwargs = self.user_plan_repository.update_plan.call_args.kwargs
        self.assertEqual(update_kwargs["plan_type_alias"], PLAN_TYPE_PM_LIFETIME_COUPLE)
        self.assertIsNone(update_kwargs["end_period"])
        payment_data = self.payment_repository.create_payment.call_args.kwargs
        self.assertEqual(payment_data["duration"], "lifetime")
        self.assertEqual(payment_data["total_price"], 0)

    def test_upgrade_to_couple_plan_with_too_many_members_is_blocked(self):
        self.user_plan_repository.count_family_members.return_value = 2

        with self.assertRaises(MaxFamilyMemberReachedException):
            self.service.upgrade_lifetime(user_id=1, code="COUPLE-CODE")

        # The code is not consumed and the plan is not changed
        self.payment_repository.update_promo_code_remaining_times.assert_not_called()
        self.user_plan_repository.cancel_plan.assert_not_called()
        self.user_plan_repository.update_plan.assert_not_called()


class LifetimeCoupleWebhookCancelTestCase(SimpleTestCase):
    def test_cancel_subscription_after_couple_upgrade_does_not_downgrade(self):
        user_plan_repository = MagicMock()
        service = PaymentHookService(
            payment_repository=MagicMock(), user_plan_repository=user_plan_repository, user_repository=MagicMock()
        )
        old_user_plan = MagicMock()
        old_user_plan.pm_plan.name = "Premium"
        user_plan_repository.get_user_plan.return_value = old_user_plan
        couple_user_plan = MagicMock()
        couple_user_plan.pm_plan.alias = PLAN_TYPE_PM_LIFETIME_COUPLE
        user_plan_repository.update_user_plan_by_id.return_value = couple_user_plan
        user_plan_repository.is_update_personal_to_enterprise.return_value = False
        # Without the lifetime guard, this user would be downgraded to Free
        user_plan_repository.is_family_member.return_value = False

        old_plan = service.webhook_cancel_subscription(user=MagicMock(user_id=1), plan=PLAN_TYPE_PM_PREMIUM)

        self.assertEqual(old_plan, "Premium")
        user_plan_repository.update_plan.assert_not_called()


@override_settings(SELF_HOSTED=True)
class FamilyMaxMemberIncludesOwnerTestCase(SimpleTestCase):
    def _add_members(self, max_allow_members: int, current_members: int, new_members: int):
        family_user_plan_orm = MagicMock()
        family_user_plan_orm.user_id = 1
        family_user_plan_orm.pm_plan.is_family_plan = True
        family_user_plan_orm.pm_plan_family.count.return_value = current_members
        # Every new member is in the family already => The insert loop skips them
        family_user_plan_orm.pm_plan_family.filter.return_value.exists.return_value = True
        family_user_plan = MagicMock()
        family_user_plan.get_max_allow_members.return_value = max_allow_members
        model_parser = MagicMock()
        model_parser.user_plan_parser.return_value.parse_user_plan.return_value = family_user_plan

        repository = UserPlanORMRepository()
        with patch.object(UserPlanORMRepository, "_get_current_plan_orm", return_value=family_user_plan_orm), \
                patch.object(UserPlanORMRepository, "_lock_family_user_plan_orm"), \
                patch.object(user_plan_repository_module.transaction, "atomic", return_value=nullcontext()), \
                patch.object(user_plan_repository_module, "ModelParser", model_parser):
            return repository.add_multiple_to_family_sharing(
                family_user_plan_id=1,
                family_members=[{"user_id": 100 + i, "email": f"member{i}@example.com"} for i in range(new_members)]
            )

    def test_couple_owner_can_add_one_member(self):
        self._add_members(max_allow_members=2, current_members=0, new_members=1)

    def test_couple_owner_can_not_add_second_member(self):
        with self.assertRaises(MaxUserPlanFamilyReachedException):
            self._add_members(max_allow_members=2, current_members=1, new_members=1)

    def test_couple_owner_can_not_add_two_members_at_once(self):
        with self.assertRaises(MaxUserPlanFamilyReachedException):
            self._add_members(max_allow_members=2, current_members=0, new_members=2)

    def test_family_owner_can_add_up_to_five_members(self):
        self._add_members(max_allow_members=6, current_members=0, new_members=5)
        with self.assertRaises(MaxUserPlanFamilyReachedException):
            self._add_members(max_allow_members=6, current_members=0, new_members=6)
