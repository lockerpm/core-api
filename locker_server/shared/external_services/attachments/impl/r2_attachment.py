import json
import traceback
from typing import Optional
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from django.conf import settings

from locker_server.shared.external_services.attachments.exceptions import AttachmentCopyException, \
    AttachmentACLException
from locker_server.shared.external_services.attachments.impl.aws_attachment import AWSAttachmentService
from locker_server.shared.log.cylog import CyLog


class R2AttachmentService(AWSAttachmentService):
    def __init__(self, access_key: str = settings.R2_ACCESS_KEY, secret_key: str = settings.R2_SECRET_KEY,
                 endpoint_url: str = settings.R2_ENDPOINT_URL, region: str = settings.R2_REGION_NAME):
        super().__init__(access_key, secret_key, endpoint_url, region)
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url,
            region_name=self.region,
            config=Config(signature_version='s3v4')
        )

    def upload_bytes_object(self, key: str, io_bytes, acl: str = "private",
                            bucket: str = settings.R2_BUCKET, tagging=None):
        try:
            if tagging:
                self.s3_client.put_object(Bucket=bucket, Key=key, Body=io_bytes, ACL=acl, Tagging=tagging)
            else:
                self.s3_client.put_object(Bucket=bucket, Key=key, Body=io_bytes, ACL=acl)
            return key
        except:
            tb = traceback.format_exc()
            CyLog.error(**{"message": "Upload IO to R2 error: {}".format(tb)})

    def get_object_content(self, object_key: str, bucket: str = settings.R2_BUCKET):
        if not bucket or not object_key:
            return
        try:
            streamed_s3_object = self.s3_client.get_object(Bucket=bucket, Key=object_key).get("Body")
        except ClientError:
            return
        content = streamed_s3_object.read().decode('utf-8')
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content

    def generate_upload_form(self, upload_file_path: str, destination: str = settings.R2_BUCKET, **metadata):
        return super().generate_upload_form(upload_file_path=upload_file_path, destination=destination, **metadata)

    def copy_file(self, old_file_path: str, new_file_path: str, source: str = settings.R2_BUCKET,
                  destination: str = settings.R2_BUCKET,  **metadata) -> str:
        """
        Copy S3 attachment
        :param old_file_path:
        :param new_file_path:
        :param source:
        :param destination:
        :param metadata:
        :return:
        """
        try:
            s3 = boto3.resource(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
                endpoint_url=self.endpoint_url,
            )
            acl = metadata.get("acl", "private")
            if acl and acl not in ["private", "public-read"]:
                raise AttachmentACLException
            copy_source = {
                'Bucket': source,
                'Key': old_file_path
            }
            extra_args = {'ACL': acl}
            s3.meta.client.copy(copy_source, destination, new_file_path, extra_args)
            if metadata.get("return_full_path", False) is True:
                return f"{settings.R2_ENDPOINT_URL}/{source}/{new_file_path}"
            return new_file_path
        except (ClientError, Exception) as e:
            tb = traceback.format_exc()
            print("TBB:::", tb)
            raise AttachmentCopyException

    def generate_onetime_url(self, file_path: str, is_cdn=False, source: str = settings.R2_BUCKET, **kwargs) -> str:
        return super().generate_onetime_url(file_path=file_path, is_cdn=is_cdn, source=source, **kwargs)
    
    def get_folder_size(self, folder_path: str, source: str = settings.R2_BUCKET) -> Optional[float]:
        return super().get_folder_size(folder_path=folder_path, source=source)
