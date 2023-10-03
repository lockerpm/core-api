from typing import Union, Dict, Optional, List, NoReturn
from abc import ABC, abstractmethod

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from locker_server.api_orm.model_parsers.wrapper import get_model_parser
from locker_server.api_orm.models.wrapper import get_enterprise_group_model
from locker_server.core.entities.enterprise.group.group import EnterpriseGroup
from locker_server.core.entities.team import team
from locker_server.core.repositories.enterprise_group_repository import EnterpriseGroupRepository
from locker_server.shared.external_services.requester.retry_requester import requester
from locker_server.shared.utils.app import now

EnterpriseGroupORM = get_enterprise_group_model()
ModelParser = get_model_parser()


class EnterpriseGroupORMRepository(EnterpriseGroupRepository):
    # ------------------------ List EnterpriseGroup resource ------------------- #
    def list_active_user_enterprise_group_ids(self, user_id: int) -> List[str]:
        return list(
            EnterpriseGroupORM.objects.filter(
                enterprise__locked=False,
                enterprise__enterprise_members__user_id=user_id,
                enterprise__enterprise_members__is_activated=True
            ).values_list('id', flat=True)
        )

    def list_enterprise_groups(self, **filters) -> List[EnterpriseGroup]:
        enterprise_id_param = filters.get("enterprise_id")
        name_param = filters.get("name")
        user_id_param = filters.get("user_id")

        if enterprise_id_param:
            enterprise_groups_orm = EnterpriseGroupORM.objects.filter(
                enterprise_id=enterprise_id_param
            ).order_by("creation_date")
        else:
            enterprise_groups_orm = EnterpriseGroupORM.objects.all()

        if name_param:
            enterprise_groups_orm = enterprise_groups_orm.filter(
                name__icontains=name_param.lower()
            )

        if user_id_param:
            enterprise_groups_orm = enterprise_groups_orm.filter(
                groups_members__member__user_id=user_id_param
            )
        return [
            ModelParser.enterprise_parser().parse_enterprise_group(enterprise_group_orm=enterprise_group_orm)
            for enterprise_group_orm in enterprise_groups_orm
        ]

    # ------------------------ Get EnterpriseGroup resource --------------------- #
    def get_by_id(self, enterprise_group_id: str) -> Optional[EnterpriseGroup]:
        try:
            enterprise_group_orm = EnterpriseGroupORM.objects.get(id=enterprise_group_id)
        except EnterpriseGroupORM.DoesNotExist:
            return None
        return ModelParser.enterprise_parser().parse_enterprise_group(enterprise_group_orm=enterprise_group_orm)

    # ------------------------ Create EnterpriseGroup resource --------------------- #
    def create_enterprise_group(self, enterprise_group_create_data: Dict) -> EnterpriseGroup:
        enterprise_group_orm = EnterpriseGroupORM.create(**enterprise_group_create_data)
        return ModelParser.enterprise_parser().parse_enterprise_group(enterprise_group_orm=enterprise_group_orm)

    # ------------------------ Update EnterpriseGroup resource --------------------- #
    def add_group_member_to_share(self, enterprise_group_ids: List, new_member_ids: List):
        enterprise_groups_orm = EnterpriseGroupORM.objects.filter(id__in=enterprise_group_ids)
        for enterprise_group_orm in enterprise_groups_orm:
            enterprise_group_member_user_ids = enterprise_group_orm.groups_members.filter(
                member_id__in=new_member_ids
            ).values_list('member__user_id', flat=True)
            sharing_groups_orm = enterprise_group_orm.sharing_groups.select_related('team').prefetch_related(
                'groups_members')
            members = [{"user_id": user_id, "key": None} for user_id in enterprise_group_member_user_ids]

            confirmed_data = []
            for sharing_group_orm in sharing_groups_orm:
                team_orm = sharing_group_orm.team
                try:
                    owner_user_orm = team_orm.team_members.get(is_primary=True).user
                except ObjectDoesNotExist:
                    continue
                collection_orm = team_orm.collections.first()
                groups = [{
                    "id": sharing_group_orm.enterprise_group_id,
                    "role": sharing_group_orm.role_id,
                    "members": members
                }]
                existed_member_users, non_existed_member_users = self.sharing_repository.add_group_members(
                    team=team, shared_collection=collection, groups=groups
                )
                if collection_orm:
                    shared_type_name = "folder"
                else:
                    cipher_orm = team_orm.ciphers.first()
                    shared_type_name = cipher_orm.type if cipher_orm else None

                url = "{}/micro_services/users".format(settings.GATEWAY_API)
                headers = {'Authorization': settings.MICRO_SERVICE_USER_AUTH}
                data_send = {"ids": existed_member_users, "emails": []}
                emails = []
                try:
                    res = requester(method="POST", url=url, headers=headers, data_send=data_send, timeout=15)
                    if res.status_code == 200:
                        users_from_id_data = res.json()
                        emails = [u.get("email") for u in users_from_id_data]
                except (requests.exceptions.RequestException, requests.exceptions.ConnectTimeout):
                    pass

                # Sending mobile notification
                if emails:
                    fcm_ids = self.device_repository.get_fcm_ids_by_user_ids(user_ids=[owner_user.user_id])
                    fcm_message = FCMRequestEntity(
                        fcm_ids=fcm_ids, priority="high",
                        data={
                            "event": FCM_TYPE_CONFIRM_SHARE_GROUP_MEMBER_ADDED,
                            "data": {
                                "share_type": shared_type_name,
                                "group_id": sharing_group.enterprise_group_id,
                                "group_name": sharing_group.name,
                                "owner_name": team.name,
                                "emails": emails
                            }
                        }
                    )
                    FCMSenderService(is_background=False).run("send_message", **{"fcm_message": fcm_message})

                confirmed_data.append({
                    "id": team.id,
                    "name": team.name,
                    "owner": owner_user.user_id,
                    "group_id": sharing_group.enterprise_group_id,
                    "group_name": sharing_group.name,
                    "shared_type_name": shared_type_name,
                    "existed_member_users": existed_member_users,
                    "non_existed_member_users": non_existed_member_users,
                })

            NotifyBackground(background=False).notify_add_group_member_to_share(data={"teams": confirmed_data})

    def update_enterprise_group(self, enterprise_group_id: str, enterprise_group_update_data: Dict) \
            -> Optional[EnterpriseGroup]:
        try:
            enterprise_group_orm = EnterpriseGroupORM.objects.get(
                id=enterprise_group_id
            )
        except EnterpriseGroupORM.DoesNotExist:
            return None
        enterprise_group_orm.name = enterprise_group_update_data.get("name", enterprise_group_orm.name)
        enterprise_group_orm.revision_date = enterprise_group_update_data.get("revision_date", now())
        enterprise_group_orm.save()
        return ModelParser.enterprise_parser().parse_enterprise_group(
            enterprise_group_orm=enterprise_group_orm
        )

    # ------------------------ Delete EnterpriseGroup resource --------------------- #
    def delete_enterprise_group_by_id(self, enterprise_group_id: str) -> NoReturn:
        try:
            enterprise_group_orm = EnterpriseGroupORM.objects.get(
                id=enterprise_group_id
            )
        except EnterpriseGroupORM.DoesNotExist:
            return
        enterprise_group_orm.full_delete()
