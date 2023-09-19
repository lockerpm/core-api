from rest_framework import serializers

from locker_server.api.v1_0.payments.serializers import FamilyMemberSerializer


class UserPlanFamilySerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = {
            "id": instance.pm_user_plan_family_id,
            "created_time": instance.created_time,
            "user_id": instance.user.user_id,
            "email": instance.email
        }
        return data


class CreateUserPlanFamilySerializer(serializers.Serializer):
    family_members = FamilyMemberSerializer(many=True, required=True)

    def validate(self, data):
        # user_repository = CORE_CONFIG["repositories"]["IUserRepository"]()
        # family_members = data.get("family_members")
        # for family_member in family_members:
        #     user_id = family_member.get("user_id")
        #     email = family_member.get("email")
        #     if user_id:
        #         try:
        #             user = user_repository.get_by_id(user_id=user_id)
        #             if not user.activated:
        #                 continue
        #         except ObjectDoesNotExist:
        #             continue
        #         current_plan = user_repository.get_current_plan(user=user, scope=settings.SCOPE_PWD_MANAGER)
        #         if current_plan.get_plan_obj().is_family_plan or current_plan.get_plan_obj().is_team_plan:
        #             raise serializers.ValidationError(detail={
        #                 "family_members": ["The user {} is in other family plan".format(email)]
        #             })

        return data
