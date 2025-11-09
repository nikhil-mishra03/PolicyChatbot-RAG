# Accept tenant info and uploaded file
# Connect to S3 with the valid credentials
# Upload file to S3 bucket
# Return response containing useful metadata like (key, bucket_name, URL)
# Surface errors in a way that can be understood by the API layer

from typing import Optional
from dataclasses import dataclass
import boto3
from app.core.config import Settings
from botocore.exceptions import BotoCoreError, ClientError
from uuid import uuid4
from app.core.logger_config import get_logger

@dataclass(slots=True)
class UploadObject:
    bucket: str
    key: str
    url: Optional[str] = None


class S3UploadService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.s3_client = boto3.client(
            's3',
            region_name=self.settings.aws_region,
            aws_access_key_id=self.settings.aws_access_key_id,
            aws_secret_access_key=self.settings.aws_secret_access_key
        )
        self.logger = get_logger(__class__.__name__)
        
    def upload_file(self, tenant_id: str, file) -> UploadObject:
        s3_client = self.s3_client
        key = f"{tenant_id}/{uuid4()}_{file.filename}"

        try:
            s3_client.upload_fileobj(
                file.file,
                self.settings.policy_bucket_name,
                key,
                ExtraArgs={"ContentType": file.content_type}                
            )
            self.logger.info(f"File uploaded successfully to S3 with key: {key}")
        except (BotoCoreError, ClientError) as exc:
            self.logger.error(f"Failed to upload file to S3 with error: {exc}")
            raise RuntimeError(f"Failed to upload file to S3 with error: {exc}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            raise RuntimeError(f"An unexpected error occurred: {e}")
        
        return UploadObject(
            bucket=self.settings.policy_bucket_name,
            key=key,
            url=f"https://{self.settings.policy_bucket_name}.s3.{self.settings.aws_region}.amazonaws.com/{key}"
        )
    

    def stream_file(self, *, s3_key: str):
        s3_client = self.s3_client
        try:
            response = s3_client.get_object(
                Bucket=self.settings.policy_bucket_name,
                Key=s3_key
            )
            return {
                'body': response['Body'],
                'content_type' : response['ContentType']
            }
        except (BotoCoreError, ClientError) as exc:
            raise RuntimeError(f"Failed to download file from S3 with err: {exc}")

