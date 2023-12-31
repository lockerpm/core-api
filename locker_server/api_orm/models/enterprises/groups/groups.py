from django.db.models import Count

from locker_server.api_orm.abstracts.enterprises.groups.groups import AbstractEnterpriseGroupORM
from locker_server.shared.constants.members import MEMBER_ROLE_OWNER
from locker_server.shared.utils.app import now


class EnterpriseGroupORM(AbstractEnterpriseGroupORM):
    class Meta(AbstractEnterpriseGroupORM.Meta):
        swappable = 'LS_ENTERPRISE_GROUP_MODEL'
        db_table = 'e_enterprise_groups'

    @classmethod
    def create(cls, **data):
        enterprise_group_orm = cls(
            name=data.get("name"),
            enterprise_id=data.get("enterprise_id"),
            created_by_id=data.get("created_by_id"),
            creation_date=data.get("creation_date", now()),
            revision_date=data.get("revision_date")
        )
        enterprise_group_orm.save()
        return enterprise_group_orm

    def full_delete(self):
        # Delete sharing group members
        sharing_group_members = self.sharing_groups.values_list('groups_members__member_id', flat=True)
        # TODO: Refactor this
        from locker_server.api_orm.models.wrapper import get_team_member_model
        TeamMemberORM = get_team_member_model()
        team_members = TeamMemberORM.objects.filter(
            id__in=list(sharing_group_members), is_added_by_group=True
        ).exclude(role_id=MEMBER_ROLE_OWNER).annotate(
            group_count=Count('groups_members')
        )
        # Filter list members have only one group. Then delete them
        team_members.filter(group_count=1).delete()

        #  Filter list members have other groups => Set role_id by other groups
        more_one_groups = team_members.filter(group_count__gt=1)
        for m in more_one_groups:
            first_group = m.groups_members.select_related('group').exclude(
                group__enterprise_group_id=self.id
            ).order_by('group_id').first()
            if first_group:
                m.role_id = first_group.group.role_id
                m.save()

        # Delete this group objects
        self.delete()
