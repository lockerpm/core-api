from typing import Optional

from locker_server.shared.external_services.attachments.attachment import AttachmentStorageService
from locker_server.shared.external_services.attachments.impl.aws_attachment import AWSAttachmentService


ATTACHMENT_AWS = "aws"


class AttachmentStorageFactory:
    @classmethod
    def get_attachment_service(cls, service_name: str, **kwargs) -> Optional[AttachmentStorageService]:
        if service_name == ATTACHMENT_AWS:
            return AWSAttachmentService(**kwargs)
        raise Exception(f"The attachment service name {service_name} does not support")
