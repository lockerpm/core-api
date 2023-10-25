from abc import ABC, abstractmethod


class EnterpriseAvatarRepository(ABC):
    # ------------------------ List EnterpriseAvatar resource ------------------- #

    # ------------------------ Get EnterpriseAvatar resource --------------------- #
    @abstractmethod
    def get_enterprise_avatar_by_enterprise_id(self, enterprise_id: str) -> str:
        pass

    # ------------------------ Create EnterpriseAvatar resource --------------------- #

    # ------------------------ Update EnterpriseAvatar resource --------------------- #
    @abstractmethod
    def update_enterprise_avatar(self, enterprise_id: str, avatar) -> str:
        pass

    # ------------------------ Delete EnterpriseAvatar resource --------------------- #
