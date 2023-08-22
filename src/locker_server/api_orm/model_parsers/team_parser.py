from locker_server.api_orm.model_parsers.wrapper_specific_model_parser import get_specific_model_parser
from locker_server.api_orm.models import *
from locker_server.core.entities.member.member_role import MemberRole
from locker_server.core.entities.member.team_member import TeamMember
from locker_server.core.entities.team.collection import Collection
from locker_server.core.entities.team.team import Team


class TeamParser:
    @classmethod
    def parse_team(cls, team_orm: TeamORM) -> Team:
        return Team(
            team_id=team_orm.id,
            name=team_orm.name,
            description=team_orm.description,
            creation_date=team_orm.creation_date,
            revision_date=team_orm.revision_date,
            locked=team_orm.locked,
            business_name=team_orm.business_name,
            key=team_orm.key,
            default_collection_name=team_orm.default_collection_name,
            public_key=team_orm.public_key,
            private_key=team_orm.private_key,
            personal_share=team_orm.personal_share
        )

    @classmethod
    def parse_member_role(cls, member_role_orm: MemberRoleORM) -> MemberRole:
        return MemberRole(name=member_role_orm.name)

    @classmethod
    def parse_team_member(cls, team_member_orm: TeamMemberORM) -> TeamMember:
        user_parser = get_specific_model_parser("UserParser")
        return TeamMember(
            team_member_id=team_member_orm.id,
            external_id=team_member_orm.external_id,
            access_time=team_member_orm.access_time,
            is_default=team_member_orm.is_default,
            is_primary=team_member_orm.is_primary,
            is_added_by_group=team_member_orm.is_added_by_group,
            hide_passwords=team_member_orm.hide_passwords,
            key=team_member_orm.key,
            reset_password_key=team_member_orm.reset_password_key,
            status=team_member_orm.status,
            email=team_member_orm.email,
            token_invitation=team_member_orm.token_invitation,
            user=user_parser.parse_user(user_orm=team_member_orm.user) if team_member_orm.user else None,
            team=cls.parse_team(team_orm=team_member_orm),
            role=cls.parse_member_role(member_role_orm=team_member_orm.role)
        )

    @classmethod
    def parse_collection(cls, collection_orm: CollectionORM) -> Collection:
        return Collection(
            collection_id=collection_orm.id,
            name=collection_orm.name,
            creation_date=collection_orm.creation_date,
            revision_date=collection_orm.revision_date,
            external_id=collection_orm.external_id,
            is_default=collection_orm.is_default,
            team=cls.parse_team(team_orm=collection_orm.team)
        )