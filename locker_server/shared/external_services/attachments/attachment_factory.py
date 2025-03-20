from typing import Optional

from locker_server.shared.external_services.attachments.attachment import AttachmentStorageService
from locker_server.shared.external_services.attachments.impl.aws_attachment import AWSAttachmentService
from locker_server.shared.external_services.attachments.impl.r2_attachment import R2AttachmentService


ATTACHMENT_AWS = "aws"
ATTACHMENT_R2 = "r2"


class AttachmentStorageFactory:
    @classmethod
    def get_attachment_service(cls, service_name: str, **kwargs) -> Optional[AttachmentStorageService]:
        if service_name == ATTACHMENT_AWS:
            return AWSAttachmentService(**kwargs)
        elif service_name == ATTACHMENT_R2:
            return R2AttachmentService(**kwargs)
        raise Exception(f"The attachment service name {service_name} does not support")
