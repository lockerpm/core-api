class AttachmentException(BaseException):
    """
    Attachment Exception
    """


class AttachmentACLException(AttachmentException):
    """
    Invalid acl
    """


class AttachmentCreateUploadFormException(AttachmentException):
    """
    Create upload form error
    """


class AttachmentCopyException(AttachmentException):
    """
    Copy file error
    """


class AttachmentListObjectsException(AttachmentException):
    """
    List objects error
    """


class AttachmentDeleteException(AttachmentException):
    """
    Delete object error
    """


class AttachmentInvalidTypeException(AttachmentException):
    """
    Invalid file extension
    """


class FileExtensionNotAllowedException(AttachmentException):
    """
    The file extension does not exist
    """
