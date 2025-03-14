from locker_server.core.exceptions.app import CoreException


class CipherAttachmentException(CoreException):
    """
    Base Exception
    """


class CipherAttachmentDoesNotExistException(CipherAttachmentException):
    """
    The cipher attachment does not exist
    """


class CipherAttachmentLimitSizeReachedException(CipherAttachmentException):
    """
    The max total size reached
    """
