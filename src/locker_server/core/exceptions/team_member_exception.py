from locker_server.core.exceptions.app import CoreException


class TeamMemberException(CoreException):
    """
    Base exception
    """


class TeamMemberDoesNotExistException(TeamMemberException):
    """
    The TeamMember does not exist
    """


class OnlyAllowOwnerUpdateException(TeamMemberException):
    """

    """