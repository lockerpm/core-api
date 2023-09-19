from locker_server.core.exceptions.app import CoreException


class ReleaseException(CoreException):
    """
    Base exception
    """


class ReleaseDoesNotExistException(ReleaseException):
    """
    The Release does not exist (not found id)
    """
