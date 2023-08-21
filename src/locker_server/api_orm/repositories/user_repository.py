from typing import Union, Dict, Optional, Tuple

from django.core.exceptions import ObjectDoesNotExist

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models import UserScoreORM
from locker_server.api_orm.models.wrapper import get_user_model, get_enterprise_member_model, get_enterprise_model, \
    get_event_model, get_cipher_model
from locker_server.core.entities.user.user import User
from locker_server.core.repositories.user_repository import UserRepository
from locker_server.shared.constants.account import ACCOUNT_TYPE_ENTERPRISE, ACCOUNT_TYPE_PERSONAL
from locker_server.shared.constants.ciphers import CIPHER_TYPE_MASTER_PASSWORD
from locker_server.shared.constants.enterprise_members import E_MEMBER_STATUS_CONFIRMED, E_MEMBER_ROLE_PRIMARY_ADMIN, \
    E_MEMBER_ROLE_ADMIN
from locker_server.shared.constants.event import EVENT_USER_BLOCK_LOGIN
from locker_server.shared.constants.policy import POLICY_TYPE_PASSWORDLESS, POLICY_TYPE_2FA
from locker_server.shared.utils.app import now, start_end_month_current

UserORM = get_user_model()
CipherORM = get_cipher_model()
EnterpriseORM = get_enterprise_model()
EnterpriseMemberORM = get_enterprise_member_model()
EventORM = get_event_model()
ModelParser = get_model_parser()


class UserORMRepository(UserRepository):
    # ------------------------ List User resource ------------------- #

    # ------------------------ Get User resource --------------------- #
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            user_orm = UserORM.objects.get(user_id=user_id)
            return ModelParser.user_parser().parse_user(user_orm=user_orm)
        except UserORM.DoesNotExist:
            return None

    def get_user_type(self, user_id: int) -> str:
        if EnterpriseMemberORM.objects.filter(user_id=user_id, status=E_MEMBER_STATUS_CONFIRMED).exists():
            return ACCOUNT_TYPE_ENTERPRISE
        return ACCOUNT_TYPE_PERSONAL

    def is_in_enterprise(self, user_id: int) -> bool:
        return EnterpriseMemberORM.objects.filter(user_id=user_id).exists()

    def is_require_passwordless(self, user_id: int,
                                require_enterprise_member_status: str = E_MEMBER_STATUS_CONFIRMED) -> bool:
        if require_enterprise_member_status:
            e_member_orm = EnterpriseMemberORM.objects.filter(
                user_id=user_id, status=require_enterprise_member_status, enterprise__locked=False
            ).first()
        else:
            e_member_orm = EnterpriseMemberORM.objects.filter(
                user_id=user_id, enterprise__locked=False
            ).first()
        e_passwordless_policy = False
        if e_member_orm:
            enterprise_orm = e_member_orm.enterprise
            policy_orm = enterprise_orm.policies.filter(policy_type=POLICY_TYPE_PASSWORDLESS, enabled=True).first()
            if policy_orm:
                e_passwordless_policy = policy_orm.policy_passwordless.only_allow_passwordless
        return e_passwordless_policy

    def is_block_by_2fa_policy(self, user_id: int, is_factor2: bool) -> bool:
        if is_factor2 is True:
            return False
        user_enterprises_orm = EnterpriseORM.objects.filter(
            enterprise_members__user_id=user_id, enterprise_members__status=E_MEMBER_STATUS_CONFIRMED
        )
        for enterprise_orm in user_enterprises_orm:
            policy_orm = enterprise_orm.policies.filter(policy_type=POLICY_TYPE_2FA, enabled=True).first()
            if not policy_orm:
                continue
            try:
                member_role = enterprise_orm.enterprise_members.get(user_id=user_id).role_id
            except ObjectDoesNotExist:
                continue
            only_admin = policy_orm.policy_2fa.only_admin
            if only_admin is False or \
                    (only_admin and member_role in [E_MEMBER_ROLE_ADMIN, E_MEMBER_ROLE_PRIMARY_ADMIN]):
                return True
        return False

    def count_failed_login_event(self, user_id: int) -> int:
        start_ts, end_ts = start_end_month_current()
        failed_login = EventORM.objects.filter(
            type=EVENT_USER_BLOCK_LOGIN, user_id=user_id,
            creation_date__gte=start_ts, creation_date__lte=end_ts
        ).count()
        return failed_login

    def has_master_pw_item(self, user_id: int) -> bool:
        return CipherORM.objects.filter(created_by_id=user_id, type=CIPHER_TYPE_MASTER_PASSWORD).exists()

    @staticmethod
    def _retrieve_or_create_user_score_orm(user_orm):
        try:
            return user_orm.user_score
        except AttributeError:
            return UserScoreORM.objects.get_or_create(user_id=user_orm.user_id, defaults={"user_id": user_orm.user_id})

    # ------------------------ Create User resource --------------------- #
    def retrieve_or_create_by_id(self, user_id, creation_date=None) -> Tuple[User, bool]:
        creation_date = now() if not creation_date else float(creation_date)
        user_orm, is_created = UserORM.objects.get_or_create(user_id=user_id, defaults={
            "user_id": user_id,
            "creation_date": creation_date
        })
        return ModelParser.user_parser().parse_user(user_orm=user_orm), is_created

    # ------------------------ Update User resource --------------------- #
    def update_user(self, user_id: int, user_update_data) -> Optional[User]:
        try:
            user_orm = UserORM.objects.get(user_id=user_id)
        except UserORM.DoesNotExist:
            return None
        scores = user_update_data.get("scores", {})
        user_orm.timeout = user_update_data.get("timeout", user_orm.timeout)
        user_orm.timeout_action = user_update_data.get("timeout_action", user_orm.timeout_action)

        user_orm.kdf = user_update_data.get("kdf", user_orm.kdf)
        user_orm.kdf_iterations = user_update_data.get("kdf_iterations", user_orm.kdf_iterations)
        user_orm.key = user_update_data.get("key", user_orm.key)
        user_orm.public_key = user_update_data.get("public_key", user_orm.public_key)
        user_orm.private_key = user_update_data.get("private_key", user_orm.private_key)
        user_orm.master_password_hint = user_update_data.get("master_password_hint", user_orm.master_password_hint)
        user_orm.master_password_score = user_update_data.get("master_password_score", user_orm.master_password_score)
        user_orm.api_key = user_update_data.get("api_key", user_orm.api_key)
        user_orm.activated = user_update_data.get("activated", user_orm.activated)
        user_orm.activated_date = user_update_data.get("activated_date", user_orm.activated_date)
        user_orm.revision_date = user_update_data.get("revision_date", user_orm.revision_date)
        user_orm.delete_account_date = user_update_data.get("delete_account_date", user_orm.delete_account_date)

        if user_update_data.get("master_password_hash"):
            user_orm.set_master_password(raw_password=user_update_data.get("master_password_hash"))

        if scores:
            user_score_orm = self._retrieve_or_create_user_score_orm(user_orm=user_orm)
            user_score_orm.cipher0 = scores.get("0", user_score_orm.cipher0)
            user_score_orm.cipher1 = scores.get("1", user_score_orm.cipher1)
            user_score_orm.cipher2 = scores.get("2", user_score_orm.cipher2)
            user_score_orm.cipher3 = scores.get("3", user_score_orm.cipher3)
            user_score_orm.cipher4 = scores.get("4", user_score_orm.cipher4)
            user_score_orm.cipher5 = scores.get("5", user_score_orm.cipher5)
            user_score_orm.cipher6 = scores.get("6", user_score_orm.cipher6)
            user_score_orm.cipher7 = scores.get("7", user_score_orm.cipher7)
            user_score_orm.save()
        user_orm.save()
        return ModelParser.user_parser().parse_user(user_orm=user_orm)

    def update_login_time_user(self, user_id: int, update_data) -> Optional[User]:
        try:
            user_orm = UserORM.objects.get(user_id=user_id)
        except UserORM.DoesNotExist:
            return None
        user_orm.login_failed_attempts = update_data.get("login_failed_attempts", user_orm.login_failed_attempts)
        user_orm.last_request_login = update_data.get("last_request_login", user_orm.last_request_login)
        user_orm.login_block_until = update_data.get("login_block_until", user_orm.login_block_until)
        user_orm.save()
        return ModelParser.user_parser().parse_user(user_orm=user_orm)

    # ------------------------ Delete User resource --------------------- #

