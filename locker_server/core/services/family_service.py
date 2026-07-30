from typing import Optional, List, Dict

from locker_server.core.entities.user_plan.pm_user_plan import PMUserPlan
from locker_server.core.exceptions.user_plan_exception import *
from locker_server.core.repositories.user_plan_repository import UserPlanRepository
from locker_server.core.repositories.user_repository import UserRepository


class FamilyService:
    """
    This class represents Use Cases related User
    """

    def __init__(self, user_repository: UserRepository,
                 user_plan_repository: UserPlanRepository):
        self.user_repository = user_repository
        self.user_plan_repository = user_plan_repository

    def is_in_family_plan(self, user_plan: PMUserPlan) -> bool:
        return self.user_plan_repository.is_in_family_plan(user_plan=user_plan)

    def list_family_members(self, user_id: int) -> Dict:
        return self.user_plan_repository.get_family_members(user_id=user_id)

    def create_multiple_family_members(self, user_id: int, family_members: List[Dict]) -> List[Dict]:
        # Checking the max number and adding the members must not interleave with a concurrent
        # request of the same owner, so both of them run in a single locked transaction of the
        # repository - the layer which is allowed to open a transaction.
        return self.user_plan_repository.add_multiple_to_family_sharing(
            family_user_plan_id=user_id, family_members=family_members
        )

    def destroy_family_member(self, user_id: int, family_member_id: int):
        family_member = self.user_plan_repository.get_family_member(
            owner_user_id=user_id, family_member_id=family_member_id
        )
        if not family_member:
            raise UserPlanFamilyDoesNotExistException
        if family_member.user is not None and family_member.user.user_id == user_id:
            raise UserPlanFamilyDoesNotExistException
        # Downgrade the plan of the member user
        family_user_id, family_email = self.user_plan_repository.delete_family_member(family_member_id=family_member_id)
        return family_user_id, family_email
