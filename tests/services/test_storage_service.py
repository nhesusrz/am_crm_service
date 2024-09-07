"""Storage service tests."""

import mimetypes
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from app.services.storage_service import public_bucket_policy

COMMON_SETTINGS = {
    "MINIO_PHOTO_BUCKET_NAME": "test-bucket",
    "MINIO_HOST": "minio",
    "MINIO_PORT": "9000",
    "MINIO_ACCESS_KEY_ID": "test-access-key",
    "MINIO_SECRET_ACCESS_KEY": "test-secret-key",
    "MINIO_SIGNATURE_VERSION": "s3v4",
    "MINIO_SERVICE_NAME": "s3",
    "MINIO_ACCESS_HOST": "http://localhost:9000",
}

FILE_BYTES = b"test file content"
FILE_NAME = "test_file.jpg"
BUCKET_NAME = COMMON_SETTINGS["MINIO_PHOTO_BUCKET_NAME"]
CONTENT_TYPE, _ = mimetypes.guess_type(FILE_NAME) or "application/octet-stream"
CONTENT_DISPOSITION = "inline"
ACCESS_HOST = COMMON_SETTINGS["MINIO_ACCESS_HOST"]
EXPECTED_URL = f"{ACCESS_HOST}/{BUCKET_NAME}/{FILE_NAME}"


@pytest.mark.asyncio
@patch("app.core.settings.load_settings")
async def test_s3_client_upload_file_success(  # noqa
    mock_load_settings,  # noqa
    mock_s3_no_buckets,
    mock_session_no_buckets,  # noqa
    s3_client,
):
    """Test the upload_file method of S3Client to ensure it uploads correctly.

    Args:
    ----
        mock_load_settings (MagicMock): Mocked load_settings function.
        mock_s3_no_buckets (AsyncMock): Mocked S3 client with no buckets.
        mock_session_no_buckets (MagicMock): Mocked aioboto3 Session with
        no buckets.
        s3_client (S3Client): The S3Client singleton instance.

    Asserts:
        str: The URL of the uploaded file matches the expected URL.

    """
    expected_url = f"{ACCESS_HOST}/{BUCKET_NAME}/{FILE_NAME}"

    url = await s3_client.upload_file(BUCKET_NAME, FILE_BYTES, FILE_NAME)

    assert url == expected_url
    mock_s3_no_buckets.create_bucket.assert_called_once_with(
        Bucket=BUCKET_NAME,
    )
    mock_s3_no_buckets.put_object.assert_called_once_with(
        Bucket=BUCKET_NAME,
        Key=FILE_NAME,
        Body=FILE_BYTES,
        ContentType=CONTENT_TYPE,
        ContentDisposition=CONTENT_DISPOSITION,
    )


@pytest.mark.asyncio
@patch("app.core.settings.load_settings")
async def test_s3_client_existing_bucket_success(  # noqa
    mock_load_settings,  # noqa
    mock_s3_existing_bucket,
    mock_session_with_buckets,  # noqa
    s3_client,
):
    """Test the upload_file method when the bucket already exists.

    Args:
    ----
        mock_load_settings (MagicMock): Mocked load_settings function.
        mock_s3_existing_bucket (AsyncMock): Mocked S3 client with an existing
        bucket.
        mock_session_with_buckets (MagicMock): Mocked aioboto3 Session with an
        existing bucket.
        s3_client (S3Client): The S3Client singleton instance.

    Asserts:
        None: Ensures the existing bucket is not recreated and the file is
        uploaded.

    """
    expected_url = f"{ACCESS_HOST}/{BUCKET_NAME}/{FILE_NAME}"

    url = await s3_client.upload_file(BUCKET_NAME, FILE_BYTES, FILE_NAME)

    assert url == expected_url
    mock_s3_existing_bucket.create_bucket.assert_not_called()
    mock_s3_existing_bucket.put_object.assert_called_once_with(
        Bucket=BUCKET_NAME,
        Key=FILE_NAME,
        Body=FILE_BYTES,
        ContentType=CONTENT_TYPE,
        ContentDisposition=CONTENT_DISPOSITION,
    )


@pytest.mark.asyncio
@patch("app.core.settings.load_settings")
async def test_s3_client_upload_file_error(  # noqa
    mock_load_settings,  # noqa
    mock_s3_no_buckets,
    mock_session_no_buckets,  # noqa
    s3_client,
):
    """Test the upload_file method to ensure it handles errors correctly.

    Args:
    ----
        mock_load_settings (MagicMock): Mocked load_settings function.
        mock_s3_no_buckets (AsyncMock): Mocked S3 client with no buckets.
        mock_session_no_buckets (MagicMock): Mocked aioboto3 Session with no
        buckets.
        s3_client (S3Client): The S3Client singleton instance.

    Asserts:
    -------
        None: Ensures that exceptions are properly raised during the upload
        process.

    """
    mock_s3_no_buckets.put_object.side_effect = ClientError(
        {
            "Error": {
                "Code": "InternalError",
                "Message": "An error occurred",
            },
        },
        "PutObject",
    )

    with pytest.raises(ClientError):
        await s3_client.upload_file(
            bucket_name=BUCKET_NAME,
            file_bytes=FILE_BYTES,
            file_name=FILE_NAME,
        )

    mock_s3_no_buckets.create_bucket.assert_called_once_with(
        Bucket=BUCKET_NAME,
    )
    mock_s3_no_buckets.put_object.assert_called_once_with(
        Bucket=BUCKET_NAME,
        Key=FILE_NAME,
        Body=FILE_BYTES,
        ContentType=CONTENT_TYPE,
        ContentDisposition=CONTENT_DISPOSITION,
    )


@pytest.mark.asyncio
@patch("app.core.settings.load_settings")
async def test_s3_client_create_bucket_error(  # noqa
    mock_load_settings,  # noqa
    mock_s3_no_buckets,
    mock_session_no_buckets,  # noqa
    s3_client,
):
    """Test the upload_file method to ensure it handles errors correctly.

    Args:
    ----
        mock_load_settings (MagicMock): Mocked load_settings function.
        mock_s3_no_buckets (AsyncMock): Mocked S3 client with no buckets.
        mock_session_no_buckets (MagicMock): Mocked aioboto3 Session with
        no buckets.
        s3_client (S3Client): The S3Client singleton instance.

    Asserts:
    -------
        None: Ensures that exceptions are properly raised during the upload
        process.

    """
    mock_s3_no_buckets.create_bucket.side_effect = ClientError(
        {
            "Error": {
                "Code": "InternalError",
                "Message": "An error occurred",
            },
        },
        "CreateBucket",
    )

    with pytest.raises(ClientError):
        await s3_client.upload_file(
            bucket_name=BUCKET_NAME,
            file_bytes=FILE_BYTES,
            file_name=FILE_NAME,
        )

    mock_s3_no_buckets.create_bucket.assert_called_once_with(
        Bucket=BUCKET_NAME,
    )
    mock_s3_no_buckets.put_bucket_policy.assert_not_called()
    mock_s3_no_buckets.put_object.assert_not_called()


@pytest.mark.asyncio
@patch("app.core.settings.load_settings")
async def test_s3_client_put_bucket_policy_error(  # noqa
    mock_load_settings,  # noqa
    mock_s3_no_buckets,
    mock_session_no_buckets,  # noqa
    s3_client,
):
    """Test the upload_file method to ensure it handles errors correctly.

    Args:
    ----
        mock_load_settings (MagicMock): Mocked load_settings function.
        mock_s3_no_buckets (AsyncMock): Mocked S3 client with no buckets.
        mock_session_no_buckets (MagicMock): Mocked aioboto3 Session with
        no buckets.
        s3_client (S3Client): The S3Client singleton instance.

    Asserts:
    -------
        None: Ensures that exceptions are properly raised during the upload
        process.

    """
    mock_s3_no_buckets.put_bucket_policy.side_effect = ClientError(
        {
            "Error": {
                "Code": "InternalError",
                "Message": "An error occurred",
            },
        },
        "PutBucketPolicy",
    )

    with pytest.raises(ClientError):
        await s3_client.upload_file(
            bucket_name=BUCKET_NAME,
            file_bytes=FILE_BYTES,
            file_name=FILE_NAME,
        )

    mock_s3_no_buckets.create_bucket.assert_called_once_with(
        Bucket=BUCKET_NAME,
    )
    mock_s3_no_buckets.put_bucket_policy.assert_called_once_with(
        Bucket=BUCKET_NAME,
        Policy=public_bucket_policy,
    )
    mock_s3_no_buckets.put_object.assert_not_called()
