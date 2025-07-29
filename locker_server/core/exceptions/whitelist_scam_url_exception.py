from locker_server.core.exceptions.app import CoreException


class WhitelistScamUrlException(CoreException):
    """
    Base exception
    """


class WhitelistScamUrlDoesNotExistException(CoreException):
    """
    Whitelist scam url not found
    """


class WhitelistScamUrlExistedException(CoreException):
    """
    Whitelist scam url already existed
    """
