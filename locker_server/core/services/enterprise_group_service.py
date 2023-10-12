from typing import List, Optional, NoReturn

from locker_server.core.entities.enterprise.enterprise import Enterprise
from locker_server.core.entities.enterprise.group.group import EnterpriseGroup
from locker_server.core.entities.enterprise.group.group_member import EnterpriseGroupMember
from locker_server.core.entities.user.user import User
from locker_server.core.exceptions.enterprise_group_exception import EnterpriseGroupDoesNotExistException
from locker_server.core.repositories.enterprise_group_member_repository import EnterpriseGroupMemberRepository
from locker_server.core.repositories.enterprise_group_repository import EnterpriseGroupRepository
from locker_server.core.repositories.enterprise_member_repository import EnterpriseMemberRepository
from locker_server.shared.constants.enterprise_members import E_MEMBER_STATUS_CONFIRMED
from locker_server.shared.utils.app import diff_list


class EnterpriseGroupService:
    """
    This class represents Use cases related EnterpriseGroupORM
    """

    def __init__(self,
                 enterprise_group_repository: EnterpriseGroupRepository,
                 enterprise_group_member_repository: EnterpriseGroupMemberRepository,
                 enterprise_member_repository: EnterpriseMemberRepository
                 ):
        self.enterprise_member_repository = enterprise_member_repository
        self.enterprise_group_repository = enterprise_group_repository
        self.enterprise_group_member_repository = enterprise_group_member_repository

    def add_group_member_to_share(self, enterprise_group_ids: List, new_member_ids: List):
        enterprise_group_member_user_ids = enterprise_group.groups_members.filter(
            member_id__in=new_member_ids
        ).values_list('member__user_id', flat=True)
        sharing_groups = enterprise_group.sharing_groups.select_related('team').prefetch_related('groups_members')
        members = [{"user_id": user_id, "key": None} for user_id in enterprise_group_member_user_ids]

        confirmed_data = []
        for sharing_group in sharing_groups:
            team = sharing_group.team
            try:
                owner_user = self.team_repository.get_primary_member(team=team).user
            except ObjectDoesNotExist:
                continue

            collection = team.collections.first()
            groups = [{
                "id": sharing_group.enterprise_group_id,
                "role": sharing_group.role_id,
                "members": members
            }]
            existed_member_users, non_existed_member_users = self.sharing_repository.add_group_members(
                team=team, shared_collection=collection, groups=groups
            )
            if collection:
                shared_type_name = "folder"
            else:
                cipher_obj = team.ciphers.first()
                shared_type_name = cipher_obj.type if cipher_obj else None

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

    def list_enterprise_groups(self, **filters) -> List[EnterpriseGroup]:
        return self.enterprise_group_repository.list_enterprise_groups(**filters)

    def get_group_by_id(self, enterprise_group_id) -> Optional[EnterpriseGroup]:
        group = self.enterprise_group_repository.get_by_id(
            enterprise_group_id=enterprise_group_id
        )
        if not group:
            raise EnterpriseGroupDoesNotExistException
        return group

    def create_group(self, enterprise: Enterprise, user: User, enterprise_group_create_data) -> EnterpriseGroup:
        enterprise_group_create_data.update({
            "enterprise_id": enterprise.enterprise_id,
            "created_by_id": user.user_id
        })
        new_group = self.enterprise_group_repository.create_enterprise_group(
            enterprise_group_create_data=enterprise_group_create_data
        )
        return new_group

    def update_group(self, group_id: str, group_update_data) -> Optional[EnterpriseGroup]:
        updated_enterprise_group = self.enterprise_group_repository.update_enterprise_group(
            enterprise_group_id=group_id,
            enterprise_group_update_data=group_update_data
        )
        if not updated_enterprise_group:
            raise EnterpriseGroupDoesNotExistException
        return updated_enterprise_group

    def delete_group_by_id(self, enterprise_group_id: str) -> bool:
        return self.enterprise_group_repository.delete_enterprise_group_by_id(
            enterprise_group_id=enterprise_group_id
        )

    def list_group_members(self, **filters) -> List[EnterpriseGroupMember]:
        return self.enterprise_group_member_repository.list_enterprise_group_members(**filters)

    def count_group_members(self, enterprise_group_id: str) -> int:
        return self.enterprise_group_member_repository.count_enterprise_group_members(enterprise_group_id)

    def update_members(self, enterprise_group: EnterpriseGroup, enterprise_member_ids: List[str]) -> List[str]:
        existed_enterprise_members = self.enterprise_member_repository.list_enterprise_members(**{
            "status": E_MEMBER_STATUS_CONFIRMED,
            "ids": enterprise_member_ids,
            "is_activated": "1"
        })
        existed_enterprise_member_ids = [member.enterprise_member_id for member in existed_enterprise_members]
        group_members = self.enterprise_group_member_repository.list_enterprise_group_members(**{
            "enterprise_group_id": enterprise_group.enterprise_group_id
        })
        existed_group_enterprise_member_ids = [
            group_member.member.enterprise_member_id for group_member in group_members
        ]
        deleted_member_ids = diff_list(existed_enterprise_member_ids, existed_enterprise_member_ids)
        new_member_ids = diff_list(existed_enterprise_members, existed_group_enterprise_member_ids)

        # Remove group members
        self.enterprise_group_member_repository.delete_multiple_by_member_ids(
            enterprise_group=enterprise_group,
            deleted_member_ids=deleted_member_ids
        )
        group_members_create_data = []
        for member_id in new_member_ids:
            group_members_create_data.append({
                "member_id": member_id,
                "group_id": enterprise_group.enterprise_group_id
            })
        self.enterprise_group_member_repository.create_multiple_group_member(
            group_members_create_data=group_members_create_data
        )
        return new_member_ids

    def add_group_member_to_share(self, enterprise_group: EnterpriseGroup, new_member_ids: List[str]):


        enterprise_group_member_user_ids = enterprise_group.groups_members.filter(
            member_id__in=new_member_ids
        ).values_list('member__user_id', flat=True)
        sharing_groups = enterprise_group.sharing_groups.select_related('team').prefetch_related('groups_members')
        members = [{"user_id": user_id, "key": None} for user_id in enterprise_group_member_user_ids]

        confirmed_data = []
        for sharing_group in sharing_groups:
            team = sharing_group.team
            try:
                owner_user = self.team_repository.get_primary_member(team=team).user
            except ObjectDoesNotExist:
                continue

            collection = team.collections.first()
            groups = [{
                "id": sharing_group.enterprise_group_id,
                "role": sharing_group.role_id,
                "members": members
            }]
            existed_member_users, non_existed_member_users = self.sharing_repository.add_group_members(
                team=team, shared_collection=collection, groups=groups
            )
            if collection:
                shared_type_name = "folder"
            else:
                cipher_obj = team.ciphers.first()
                shared_type_name = cipher_obj.type if cipher_obj else None

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
