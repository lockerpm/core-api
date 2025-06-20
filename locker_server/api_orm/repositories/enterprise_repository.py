import os
from typing import Union, Dict, Optional, List

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_user_model, get_enterprise_domain_model, \
    get_enterprise_member_model, get_enterprise_group_member_model, get_enterprise_model, get_event_model
from locker_server.core.entities.enterprise.enterprise import Enterprise
from locker_server.core.repositories.enterprise_repository import EnterpriseRepository
from locker_server.shared.constants.enterprise_members import E_MEMBER_ROLE_MEMBER, E_MEMBER_STATUS_CONFIRMED, \
    E_MEMBER_STATUS_INVITED
from locker_server.shared.utils.app import now

UserORM = get_user_model()
DomainORM = get_enterprise_domain_model()
EnterpriseMemberORM = get_enterprise_member_model()
EnterpriseGroupMemberORM = get_enterprise_group_member_model()
# PMPlanORM = get_plan_model()
# PMUserPlanORM = get_user_plan_model()
# EnterpriseMemberRoleORM = get_enterprise_member_role_model()
# EnterpriseMemberORM = get_enterprise_member_model()
EnterpriseORM = get_enterprise_model()
EventORM = get_event_model()
ModelParser = get_model_parser()


class EnterpriseORMRepository(EnterpriseRepository):
    @staticmethod
    def _get_user_orm(user_id: int) -> Optional[UserORM]:
        try:
            return UserORM.objects.get(user_id=user_id)
        except UserORM.DoesNotExist:
            return None

    @staticmethod
    def _get_enterprise_orm(enterprise_id: str) -> Optional[UserORM]:
        try:
            return EnterpriseORM.objects.get(id=enterprise_id)
        except EnterpriseORM.DoesNotExist:
            return None

    # ------------------------ List Enterprise resource ------------------- #
    def list_enterprises(self, **filters) -> List[Enterprise]:
        locked_param = filters.get("locked")
        enterprises_orm = EnterpriseORM.objects.all().order_by('creation_date')
        if locked_param is not None:
            enterprises_orm = enterprises_orm.filter(locked=locked_param)
        return [
            ModelParser.enterprise_parser().parse_enterprise(enterprise_orm=enterprise_orm)
            for enterprise_orm in enterprises_orm
        ]

    def list_enterprise_ids(self, **filters) -> List:
        locked_param = filters.get("locked")
        if locked_param is not None:
            if locked_param == "1":
                enterprises_orm = EnterpriseORM.objects.filter(locked=True)
            else:
                enterprises_orm = EnterpriseORM.objects.filter(locked=False)
        else:
            enterprises_orm = EnterpriseORM.objects.all()
        return list(enterprises_orm.order_by("id").values("id", "name", "locked").distinct())

    def list_user_enterprises(self, user_id: int, **filter_params) -> List[Enterprise]:
        status_param = filter_params.get("status")
        if status_param is not None:
            enterprises_orm = EnterpriseORM.objects.filter(
                enterprise_members__user_id=user_id, enterprise_members__status=status_param
            ).order_by('-creation_date')
        else:
            enterprises_orm = EnterpriseORM.objects.filter(
                enterprise_members__user_id=user_id
            ).order_by('-creation_date')
        is_activated_param = filter_params.get("is_activated")
        if is_activated_param is not None:
            enterprises_orm = enterprises_orm.filter(
                enterprise_members__user_id=user_id,
                enterprise_members__is_activated=is_activated_param
            )
        return [ModelParser.enterprise_parser().parse_enterprise(enterprise_orm=enterprise_orm)
                for enterprise_orm in enterprises_orm]

    def list_user_enterprise_ids(self, user_id: int, **filter_params) -> List[str]:
        enterprises_orm = EnterpriseORM.objects.filter(
            enterprise_members__user_id=user_id
        ).order_by('-creation_date')
        status_param = filter_params.get("status")
        is_activated_param = filter_params.get("is_activated")
        if status_param:
            enterprises_orm = enterprises_orm.filter(enterprise_members__status=status_param)
        if is_activated_param is not None:
            enterprises_orm = enterprises_orm.filter(enterprise_members__is_activated=is_activated_param)
        return list(set(enterprises_orm.values_list('id', flat=True)))

    # ------------------------ Get Enterprise resource --------------------- #
    def get_enterprise_by_id(self, enterprise_id: str) -> Optional[Enterprise]:
        try:
            enterprise_orm = EnterpriseORM.objects.get(id=enterprise_id)
        except EnterpriseORM.DoesNotExist:
            return None
        return ModelParser.enterprise_parser().parse_enterprise(enterprise_orm=enterprise_orm)

    def get_enterprise_avatar(self, enterprise_id: str) -> Optional[str]:
        try:
            enterprise_orm = EnterpriseORM.objects.get(id=enterprise_id)
            avatar_url = enterprise_orm.avatar.url
            return avatar_url
        except EnterpriseORM.DoesNotExist:
            return None

    # ------------------------ Create Enterprise resource --------------------- #
    def create_enterprise(self, enterprise_create_data: Dict) -> Enterprise:
        members_data = enterprise_create_data.pop("members", [])
        new_enterprise_orm = EnterpriseORM.create(**enterprise_create_data)
        # Create team members
        new_members_orm = []
        for member_data in members_data:
            new_members_orm.append(EnterpriseMemberORM(
                enterprise_id=new_enterprise_orm.id,
                role_id=member_data.get("role_id", E_MEMBER_ROLE_MEMBER),
                user_id=member_data.get('user_id'),
                status=member_data.get("status", E_MEMBER_STATUS_INVITED),
                is_primary=member_data.get("is_primary", False),
                is_default=member_data.get("is_default", False),
                email=member_data.get("email", None),
                token_invitation=member_data.get("token_invitation", None),
            ))
        EnterpriseMemberORM.objects.bulk_create(new_members_orm, ignore_conflicts=True)
        return ModelParser.enterprise_parser().parse_enterprise(enterprise_orm=new_enterprise_orm)

    # ------------------------ Update Enterprise resource --------------------- #
    def update_enterprise(self, enterprise_id: str, enterprise_update_data) -> Optional[Enterprise]:
        try:
            enterprise_orm = EnterpriseORM.objects.get(id=enterprise_id)
        except EnterpriseORM.DoesNotExist:
            return None
        enterprise_orm.name = enterprise_update_data.get("name", enterprise_orm.name)
        enterprise_orm.description = enterprise_update_data.get(
            "description", enterprise_orm.description
        )
        enterprise_orm.enterprise_name = enterprise_update_data.get(
            "enterprise_name", enterprise_orm.enterprise_name
        )
        enterprise_orm.enterprise_address1 = enterprise_update_data.get(
            "enterprise_address1",
            enterprise_orm.enterprise_address1
        )
        enterprise_orm.enterprise_address2 = enterprise_update_data.get(
            "enterprise_address2",
            enterprise_orm.enterprise_address2
        )
        enterprise_orm.enterprise_phone = enterprise_update_data.get(
            "enterprise_phone",
            enterprise_orm.enterprise_phone
        )
        enterprise_orm.enterprise_country = enterprise_update_data.get(
            "enterprise_country",
            enterprise_orm.enterprise_country
        )
        enterprise_orm.enterprise_postal_code = enterprise_update_data.get(
            "enterprise_postal_code",
            enterprise_orm.enterprise_postal_code
        )
        enterprise_orm.enterprise_registration_number = enterprise_update_data.get(
            "enterprise_registration_number",
            enterprise_orm.enterprise_registration_number,
        )
        enterprise_orm.enterprise_registration_date = enterprise_update_data.get(
            "enterprise_registration_date",
            enterprise_orm.enterprise_registration_date,
        )
        enterprise_orm.enterprise_entity_type = enterprise_update_data.get(
            "enterprise_entity_type",
            enterprise_orm.enterprise_entity_type,
        )
        enterprise_orm.enterprise_vat_id = enterprise_update_data.get(
            "enterprise_vat_id",
            enterprise_orm.enterprise_vat_id,
        )
        enterprise_orm.init_seats = enterprise_update_data.get("init_seats", enterprise_orm.init_seats)
        enterprise_orm.init_seats_expired_time = enterprise_update_data.get(
            "init_seats_expired_time",
            enterprise_orm.init_seats_expired_time
        )
        enterprise_orm.revision_date = now()

        enterprise_orm.save()
        return ModelParser.enterprise_parser().parse_enterprise(enterprise_orm=enterprise_orm)

    def update_enterprise_avatar(self, enterprise_id: str, avatar) -> str:
        try:
            enterprise_orm = EnterpriseORM.objects.get(id=enterprise_id)
            old_avatar = enterprise_orm.avatar
            if old_avatar is not None:
                try:
                    os.remove(old_avatar.path)
                except (FileNotFoundError, ValueError):
                    pass
            enterprise_orm.avatar = avatar
            enterprise_orm.save()
            return enterprise_orm.avatar.url
        except EnterpriseORM.DoesNotExist:
            return None

    # ------------------------ Delete Enterprise resource --------------------- #
    def delete_completely(self, enterprise: Enterprise):
        enterprise_id = enterprise.enterprise_id
        self.clear_data(enterprise=enterprise)
        try:
            EnterpriseORM.objects.get(id=enterprise_id).delete()
        except EnterpriseORM.DoesNotExist:
            pass
        # Delete all events
        EventORM.objects.filter(team_id=enterprise_id).delete()

    def clear_data(self, enterprise: Enterprise):
        enterprise_orm = self._get_enterprise_orm(enterprise_id=enterprise.enterprise_id)
        enterprise_orm.enterprise_members.order_by('id').delete()
        enterprise_orm.policies.order_by('id').delete()
        enterprise_orm.domains.all().order_by('id').delete()
        groups_orm = enterprise_orm.groups.order_by('id')
        for group_orm in groups_orm:
            group_orm.full_delete()
