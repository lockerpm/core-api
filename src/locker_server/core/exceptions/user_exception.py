from locker_server.core.exceptions.app import CoreException


class UserException(CoreException):
    """
    Base exception
    """


class UserDoesNotExistException(UserException):
    """
    The User does not exist (not found id or not found username, etc...)
    """


class UserAuthFailedException(UserException):
    """
    The User device access token is not valid
    """
