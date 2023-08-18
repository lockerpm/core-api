from typing import Optional

from locker_server.core.entities.enterprise.enterprise import Enterprise
from locker_server.core.entities.user.user import User
from locker_server.core.entities.user_plan.pm_user_plan import PMUserPlan
from locker_server.core.exceptions.user_exception import UserDoesNotExistException
from locker_server.core.repositories.enterprise_member_repository import EnterpriseMemberRepository
from locker_server.core.repositories.payment_repository import PaymentRepository
from locker_server.core.repositories.plan_repository import PlanRepository
from locker_server.core.repositories.team_member_repository import TeamMemberRepository
from locker_server.core.repositories.user_plan_repository import UserPlanRepository
from locker_server.core.repositories.user_repository import UserRepository
from locker_server.shared.constants.enterprise_members import E_MEMBER_STATUS_CONFIRMED
from locker_server.shared.constants.transactions import *
from locker_server.shared.external_services.locker_background.background_factory import BackgroundFactory
from locker_server.shared.external_services.locker_background.constants import BG_NOTIFY
from locker_server.shared.utils.app import secure_random_string, now


class UserService:
    """
    This class represents Use Cases related User
    """

    def __init__(self, user_repository: UserRepository, user_plan_repository: UserPlanRepository,
                 payment_repository: PaymentRepository, plan_repository: PlanRepository,
                 team_member_repository: TeamMemberRepository,
                 enterprise_member_repository: EnterpriseMemberRepository):
        self.user_repository = user_repository
        self.user_plan_repository = user_plan_repository
        self.payment_repository = payment_repository
        self.plan_repository = plan_repository
        self.team_member_repository = team_member_repository
        self.enterprise_member_repository = enterprise_member_repository

    def get_current_plan(self, user: User) -> PMUserPlan:
        return self.user_plan_repository.get_user_plan(user_id=user.user_id)

    def get_user_type(self, user: User) -> str:
        return self.user_repository.get_user_type(user_id=user.user_id)

    def get_default_enterprise(self, user_id: int, enterprise_name: str = None,
                               create_if_not_exist=False) -> Optional[Enterprise]:
        return self.user_plan_repository.get_default_enterprise(
            user_id=user_id, enterprise_name=enterprise_name, create_if_not_exist=create_if_not_exist
        )

    def is_blocked_by_source(self, user: User, utm_source: str) -> bool:
        return self.payment_repository.is_blocked_by_source(user_id=user.user_id, utm_source=utm_source)

    def update_user(self, user_id: int, user_update_data) -> Optional[User]:
        user = self.user_repository.update_user(user_id=user_id, user_update_data=user_update_data)
        if not user:
            raise UserDoesNotExistException
        return user

    def retrieve_by_id(self, user_id: int) -> User:
        user = self.user_repository.get_user_by_id(user_id=user_id)
        if not user:
            raise UserDoesNotExistException
        return user

    def retrieve_or_create_by_id(self, user_id: int) -> User:
        user, is_created = self.user_repository.retrieve_or_create_by_id(user_id=user_id)
        if is_created is True:
            self.get_current_plan(user=user)
        return user

    def register_user(self, user_id: int, master_password_hash: str, key: str, keys, **kwargs):
        user = self.retrieve_or_create_by_id(user_id=user_id)

        user_new_creation_data = {
            "kdf": kwargs.get("kdf", 0),
            "kdf_iterations": kwargs.get("kdf_iterations", 100000),
            "key": key,
            "public_key": keys.get("public_key"),
            "private_key": keys.get("private_key"),
            "master_password_hash": master_password_hash,
            "master_password_hint": kwargs.get("master_password_hint", ""),
            "master_password_score": kwargs.get("score") or kwargs.get("master_password_score"),
            "api_key": secure_random_string(length=30),
            "activated": True,
            "activated_date": now(),
            "revision_date": now(),
            "delete_account_date": None,
        }
        user = self.user_repository.update_user(user_id=user.user_id, user_update_data=user_new_creation_data)
        current_plan = self.get_current_plan(user=user)
        # Upgrade trial plan
        trial_plan = kwargs.get("trial_plan")
        is_trial_promotion = kwargs.get("is_trial_promotion", False)
        enterprise_name = kwargs.get("enterprise_name")

        # Upgrade trial plan
        if trial_plan and trial_plan != PLAN_TYPE_PM_FREE:
            trial_plan_obj = self.plan_repository.get_plan_by_alias(alias=trial_plan)
            if trial_plan_obj.is_team_plan is False:
                if current_plan.is_personal_trial_applied() is False:
                    end_period = now() + TRIAL_PERSONAL_PLAN
                    trial_duration = TRIAL_PERSONAL_DURATION_TEXT
                    if is_trial_promotion is True and trial_plan_obj.alias == PLAN_TYPE_PM_FAMILY:
                        end_period = now() + TRIAL_PROMOTION
                        trial_duration = TRIAL_PROMOTION_DURATION_TEXT
                    plan_metadata = {
                        "start_period": now(),
                        "end_period": end_period
                    }
                    self.user_plan_repository.update_plan(
                        user_id=user.user_id, plan_type_alias=trial_plan_obj.alias,
                        duration=DURATION_MONTHLY, **plan_metadata
                    )
                    self.user_plan_repository.set_personal_trial_applied(user_id=user_id, applied=True, platform="web")
                    # Send trial mail
                    BackgroundFactory.get_background(
                        bg_name=BG_NOTIFY, background=True
                    ).run(
                        func_name="trial_successfully", **{
                            "user_id": user.user_id,
                            "plan": trial_plan_obj.alias,
                            "payment_method": None,
                            "duration": trial_duration,
                        }
                    )

            # Enterprise plan
            else:
                if self.user_repository.is_in_enterprise(user_id=user_id) is False and \
                        current_plan.pm_plan.alias == PLAN_TYPE_PM_FREE:
                    end_period = now() + TRIAL_TEAM_PLAN
                    number_members = TRIAL_TEAM_MEMBERS
                    plan_metadata = {
                        "start_period": now(),
                        "end_period": end_period,
                        "number_members": number_members,
                        "enterprise_name": enterprise_name
                    }
                    self.user_plan_repository.update_plan(
                        user_id=user.user_id, plan_type_alias=trial_plan_obj.alias, duration=DURATION_MONTHLY,
                        **plan_metadata
                    )
                    self.user_plan_repository.set_enterprise_trial_applied(user_id=user_id, applied=True)
                    # Send trial enterprise mail here
                    BackgroundFactory.get_background(bg_name=BG_NOTIFY, background=False).run(
                        func_name="trial_enterprise_successfully", **{"user_id": user.user_id}
                    )

        # Upgrade plan if the user is a family member
        self.user_plan_repository.upgrade_member_family_plan(user=user)
        # Update sharing confirmation
        self.team_member_repository.sharing_invitations_confirm(user=user)
        # Update enterprise invitations
        self.enterprise_member_repository.enterprise_invitations_confirm(user=user)
        # TODO: Update enterprise share groups
        self.enterprise_member_repository.enterprise_share_groups_confirm(user=user)
        # Update lifetime mail
        if user.saas_source:
            if current_plan.pm_plan.alias == PLAN_TYPE_PM_LIFETIME:
                BackgroundFactory.get_background(bg_name=BG_NOTIFY).run(
                    func_name="notify_locker_mail", **{
                        "user_ids": [user.user_id],
                        "job": "upgraded_to_lifetime_from_code",
                        "service_name": user.saas_source,
                    }
                )
            else:
                BackgroundFactory.get_background(bg_name=BG_NOTIFY).run(
                    func_name="notify_locker_mail", **{
                        "user_ids": [user.user_id],
                        "job": "upgraded_from_code_promo",
                        "service_name": user.saas_source,
                        "plan": current_plan.pm_plan.alias
                    }
                )

        return user

    def invitation_confirmation(self, user_id: int, email: str = None) -> User:
        user = self.retrieve_or_create_by_id(user_id=user_id)
        # Update sharing confirmation
        self.team_member_repository.sharing_invitations_confirm(user=user, email=email)
        # Update enterprise invitations
        self.enterprise_member_repository.enterprise_invitations_confirm(user=user, email=email)
        return user

    def is_require_passwordless(self, user_id: int,
                                require_enterprise_member_status: str = E_MEMBER_STATUS_CONFIRMED) -> bool:
        return self.user_repository.is_require_passwordless(
            user_id=user_id, require_enterprise_member_status=require_enterprise_member_status
        )
