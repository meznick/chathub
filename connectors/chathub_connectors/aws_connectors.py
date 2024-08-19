from typing import Optional

import boto3
from botocore.exceptions import NoCredentialsError, ClientError

from chathub_connectors import LOGGER


class S3Client:
    """
    AWS S3 client.

    Example usage:
    s3_client = S3Client('your-access-key-id', 'your-secret-access-key', 'your-bucket-name')
    s3_client.upload_file('path/to/local/file', 'path/to/s3/file')
    s3_client.download_file('path/to/s3/file', 'path/to/local/file')
    """

    def __init__(
            self,
            aws_access_key_id: str,
            aws_secret_access_key: str,
            bucket_name: str,
            region_name: Optional[str] = 'eu-central-1',
    ):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.bucket_name = bucket_name

    def upload_file(self, local_file_path: str, s3_file_path: str):
        try:
            self.s3.upload_file(local_file_path, self.bucket_name, s3_file_path)
            LOGGER.debug(f"File {local_file_path} uploaded to {s3_file_path}")
        except FileNotFoundError:
            LOGGER.error(f"The file {local_file_path} was not found")
        except NoCredentialsError:
            LOGGER.error("Credentials not available")
        except ClientError as e:
            LOGGER.error(f"Failed to upload {local_file_path}: {e}")

    def download_file(self, s3_file_path: str, local_file_path: str):
        try:
            self.s3.download_file(self.bucket_name, s3_file_path, local_file_path)
            LOGGER.debug(f"File {s3_file_path} downloaded to {local_file_path}")
        except NoCredentialsError:
            LOGGER.error("Credentials not available")
        except ClientError as e:
            LOGGER.error(f"Failed to download {s3_file_path}: {e}")
