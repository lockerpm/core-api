from locker_server.core.exceptions.app import CoreException


class CipherException(CoreException):
    """
    Base exception
    """


class CipherDoesNotExistException(CipherException):
    """
    The Cipher does not exist
    """


class FolderDoesNotExistException(CipherException):
    """
    The Folder does not exist
    """


class CipherMaximumReachedException(CipherException):
    """
    The maximum number of items is reached. Please check your trash if any"
    """