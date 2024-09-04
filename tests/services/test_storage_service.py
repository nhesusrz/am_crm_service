"""Storage service tests."""

import mimetypes
from unittest.mock import AsyncMock, patch

import pytest
from botocore.exceptions import ClientError


@pytest.mark.asyncio
@patch("aioboto3.Session")
@patch("app.core.settings.load_settings")
async def test_s3_client_upload_file(  # noqa
    mock_load_settings,
    mock_session,
    s3_client,
):
    """Test the upload_file method of S3Client to ensure it uploads files.

    correctly.

    Args:
    ----
        mock_load_settings (MagicMock): Mocked load_settings function.
        mock_session (MagicMock): Mocked aioboto3 Session class.
        s3_client (S3Client): The S3Client singleton instance.

    Asserts:
        str: The URL of the uploaded file matches the expected URL.

    """
    mock_load_settings.return_value.MINIO_PHOTO_BUCKET_NAME = "test-bucket"
    mock_load_settings.return_value.MINIO_HOST = "localhost"
    mock_load_settings.return_value.MINIO_PORT = "9000"
    mock_load_settings.return_value.MINIO_ACCESS_KEY_ID = "test-access-key"
    mock_load_settings.return_value.MINIO_SECRET_ACCESS_KEY = "test-secret-key"
    mock_load_settings.return_value.MINIO_SIGNATURE_VERSION = "s3v4"
    mock_load_settings.return_value.MINIO_SERVICE_NAME = "s3"

    mock_s3 = AsyncMock()
    mock_session.return_value.client.return_value.__aenter__.return_value = (
        mock_s3
    )
    mock_s3.list_buckets.return_value = {"Buckets": []}
    mock_s3.create_bucket.return_value = {}
    mock_s3.put_object.return_value = {}

    file_bytes = b"test file content"
    file_name = "test_file.jpg"
    bucket_name = "test-bucket"
    content_type, _ = (
        mimetypes.guess_type(file_name) or "application/octet-stream"
    )

    expected_url = f"http://localhost:9000/{bucket_name}/{file_name}"

    url = await s3_client.upload_file(bucket_name, file_bytes, file_name)

    assert url == expected_url
    mock_s3.create_bucket.assert_called_once_with(Bucket=bucket_name)
    mock_s3.put_object.assert_called_once_with(
        Bucket=bucket_name,
        Key=file_name,
        Body=file_bytes,
        ContentType=content_type,
        ContentDisposition="inline",
    )


@pytest.mark.asyncio
@patch("aioboto3.Session")
@patch("app.core.settings.load_settings")
async def test_s3_client_existing_bucket(  # noqa
    mock_load_settings,
    mock_session,
    s3_client,
):
    """Test the upload_file method when the bucket already exists.

    Args:
    ----
        mock_load_settings (MagicMock): Mocked load_settings function.
        mock_session (MagicMock): Mocked aioboto3 Session class.
        s3_client (S3Client): The S3Client singleton instance.

    Asserts:
        None: Ensures the existing bucket is not recreated and the file is
        uploaded.

    """
    # Mock settings
    mock_load_settings.return_value.MINIO_PHOTO_BUCKET_NAME = "test-bucket"
    mock_load_settings.return_value.MINIO_ACCESS_HOST = "localhost"
    mock_load_settings.return_value.MINIO_PORT = "9000"
    mock_load_settings.return_value.MINIO_ACCESS_KEY_ID = "test-access-key"
    mock_load_settings.return_value.MINIO_SECRET_ACCESS_KEY = "test-secret-key"
    mock_load_settings.return_value.MINIO_SIGNATURE_VERSION = "s3v4"
    mock_load_settings.return_value.MINIO_SERVICE_NAME = "s3"

    # Mock S3 client methods
    mock_s3 = AsyncMock()
    mock_session.return_value.client.return_value.__aenter__.return_value = (
        mock_s3
    )
    mock_s3.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
    mock_s3.create_bucket.return_value = {}
    mock_s3.put_object.return_value = {}

    file_bytes = b"test file content"
    external_host = "localhost"
    external_port = 9000
    file_name = "test_file.jpg"
    bucket_name = "test-bucket"
    content_type, _ = (
        mimetypes.guess_type(file_name) or "application/octet-stream"
    )

    expected_url = (
        f"http://{external_host}:{external_port}/{bucket_name}/{file_name}"
    )

    # Test upload_file
    url = await s3_client.upload_file(bucket_name, file_bytes, file_name)

    assert url == expected_url
    mock_s3.create_bucket.assert_not_called()
    mock_s3.put_object.assert_called_once_with(
        Bucket=bucket_name,
        Key=file_name,
        Body=file_bytes,
        ContentType=content_type,
        ContentDisposition="inline",
    )


@pytest.mark.asyncio
@patch("aioboto3.Session")
@patch("app.core.settings.load_settings")
async def test_s3_client_upload_file_error(  # noqa
    mock_load_settings,
    mock_session,
    s3_client,
):
    """Test the upload_file method to ensure it handles errors correctly.

    Args:
    ----
        mock_load_settings (MagicMock): Mocked load_settings function.
        mock_session (MagicMock): Mocked aioboto3 Session class.
        s3_client (S3Client): The S3Client singleton instance.

    Asserts:
        None: Ensures that exceptions are properly raised during the upload
        process.

    """
    mock_load_settings.return_value.MINIO_PHOTO_BUCKET_NAME = "test-bucket"
    mock_load_settings.return_value.MINIO_ACCESS_HOST = "localhost"
    mock_load_settings.return_value.MINIO_PORT = "9000"
    mock_load_settings.return_value.AWS_ACCESS_KEY_ID = "test-access-key"
    mock_load_settings.return_value.AWS_SECRET_ACCESS_KEY = "test-secret-key"
    mock_load_settings.return_value.MINIO_SIGNATURE_VERSION = "s3v4"
    mock_load_settings.return_value.MINIO_SERVICE_NAME = "s3"

    mock_s3 = AsyncMock()
    mock_session.return_value.client.return_value.__aenter__.return_value = (
        mock_s3
    )
    mock_s3.list_buckets.return_value = {"Buckets": []}
    mock_s3.create_bucket.return_value = {}

    # Simulate an error during the put_object call
    mock_s3.put_object.side_effect = ClientError(
        {
            "Error": {
                "Code": "InternalError",
                "Message": "An error occurred",
            },
        },
        "PutObject",
    )

    file_bytes = b"test file content"
    file_name = "test_file.jpg"
    bucket_name = "test-bucket"
    content_type, _ = (
        mimetypes.guess_type(file_name) or "application/octet-stream"
    )

    # Ensure that ClientError is raised due to put_object error
    with pytest.raises(ClientError):
        await s3_client.upload_file(bucket_name, file_bytes, file_name)

    # Verify that the bucket creation was attempted
    mock_s3.create_bucket.assert_called_once_with(Bucket=bucket_name)
    # Verify that put_object was called
    mock_s3.put_object.assert_called_once_with(
        Bucket=bucket_name,
        Key=file_name,
        Body=file_bytes,
        ContentType=content_type,
        ContentDisposition="inline",
    )
