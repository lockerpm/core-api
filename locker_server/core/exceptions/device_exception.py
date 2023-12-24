from locker_server.core.exceptions.app import CoreException


class DeviceException(CoreException):
    """
    Base Device Exception
    """


class DeviceDoesNotExistException(DeviceException):
    """
    The device does not exist
    """


class DeviceFactor2Exception(CoreException):
    """
    Base Device Factor2 Exception
    """


class DeviceFactor2DoesNotExistException(DeviceFactor2Exception):
    """
    The device factor2 does not exist
    """
