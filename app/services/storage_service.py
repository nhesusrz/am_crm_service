"""S3 Client Module.

This module defines the `S3Client` class, which is a singleton designed
to interact with an S3-compatible storage service. The class provides
functionality to upload files to a specified S3 bucket and manage
bucket creation. The `S3Client` uses configuration settings for
initialization and ensures that only one instance of the client
is used throughout the application to maintain consistency and avoid
potential conflicts.

Imports:
- aioboto3: Asynchronous boto3 client for interacting with AWS S3.
- botocore.client.Config: Configuration options for the boto3 client.
- asyncio: Asynchronous programming support.
- app.core.settings: Configuration settings for the S3 client.

Classes:
- S3Client: Singleton class for managing the S3 client instance and
providing methods to upload files and manage buckets.
"""

import asyncio
import json
import mimetypes

import aioboto3
from botocore.client import Config

from app.core import logger, settings

logger = logger.get_logger()
app_settings = settings.load_settings()

public_bucket_policy = json.dumps(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{
                    app_settings.MINIO_PHOTO_BUCKET_NAME
                }/*",
            },
        ],
    },
)


class S3Client:
    """Singleton class to interact with the S3-compatible storage service."""

    _instance = None
    _init_lock = asyncio.Lock()

    # Load settings once and store them in class-level constants
    _minio_service_name = app_settings.MINIO_SERVICE_NAME
    _minio_bucket_name = app_settings.MINIO_PHOTO_BUCKET_NAME
    _endpoint_url = (
        f"http://{app_settings.MINIO_ACCESS_HOST}:{app_settings.MINIO_PORT}"
    )
    _minio_access_key_id = app_settings.MINIO_ACCESS_KEY_ID
    _minio_secret_access_key = app_settings.MINIO_SECRET_ACCESS_KEY
    _minio_signature_version = app_settings.MINIO_SIGNATURE_VERSION

    def __new__(cls):
        """Create or return the singleton instance of the S3Client class.

        Returns
        -------
            S3Client: The singleton instance of the S3Client class.

        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def upload_file(
        self,
        bucket_name: str,
        file_bytes: bytes,
        file_name: str,
    ) -> str:
        """Upload a file to the specified S3 bucket and return the file URL.

        Args:
        ----
            bucket_name (str): The name of the S3 bucket where the file will be
            uploaded.
            file_bytes (bytes): The content of the file to be uploaded.
            file_name (str): The name to use for the file in the bucket.

        Returns:
        -------
            str: The URL of the uploaded file.

        Raises:
        ------
            Exception: Any exception raised during the upload process.

        """
        async with S3Client._init_lock:  # noqa
            async with aioboto3.Session().client(  # type: ignore
                self._minio_service_name,
                endpoint_url=self._endpoint_url,
                aws_access_key_id=self._minio_access_key_id,
                aws_secret_access_key=self._minio_secret_access_key,
                config=Config(signature_version=self._minio_signature_version),
            ) as s3:
                try:
                    existing_buckets = await s3.list_buckets()
                except Exception as e:
                    logger.error(f"Error listing buckets: {e}")
                    raise e
                if bucket_name not in [
                    bucket["Name"] for bucket in existing_buckets["Buckets"]
                ]:
                    try:
                        await s3.create_bucket(Bucket=bucket_name)
                        await s3.put_bucket_policy(
                            Bucket=bucket_name,
                            Policy=public_bucket_policy,
                        )
                    except Exception as e:
                        logger.error(f"Error creating bucket: {e}")
                        raise e
                    logger.info(f"Bucket '{bucket_name}' created.")
                else:
                    logger.info(f"Bucket '{bucket_name}' already exists.")
                content_type, _ = (
                    mimetypes.guess_type(file_name)
                    or "application/octet-stream"
                )
                try:
                    await s3.put_object(
                        Bucket=bucket_name,
                        Key=file_name,
                        Body=file_bytes,
                        ContentType=content_type,
                        ContentDisposition="inline",
                    )
                except Exception as e:
                    logger.error(f"Error uploading the file: {e}")
                    raise e
                logger.info(f"The file '{file_name}' is already uploaded.")
                return f"{self._endpoint_url}/{bucket_name}/{file_name}"
