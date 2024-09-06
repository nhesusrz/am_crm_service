"""Settings tests."""

import pytest
from pydantic import ValidationError
from sqlalchemy.engine import URL

from app.core.settings import Settings, load_default_settings, load_settings

EXPECTED_PROJECT_NAME = "Customer Management API"
EXPECTED_API_V1_STR = "/api/v1"
EXPECTED_POSTGRES_HOST = "localhost"
EXPECTED_POSTGRES_PORT = 5432
EXPECTED_POSTGRES_USER = "postgres"
EXPECTED_POSTGRES_PASSWORD = "postgres"
EXPECTED_POSTGRES_DB = "database_name"
EXPECTED_SQLALCHEMY_POOL_SIZE = 10
EXPECTED_SQLALCHEMY_MAX_OVERFLOW = 20
EXPECTED_TOKEN_SECRET_KEY = "your_secret_key"
EXPECTED_TOKEN_ALGORITHM = "HS256"
EXPECTED_ACCESS_TOKEN_EXPIRE_MINUTES = 30
EXPECTED_PASS_ALGORITHM = "pbkdf2_sha256"
EXPECTED_MINIO_SERVICE_NAME = "s3"
EXPECTED_MINIO_HOST = "localhost"
EXPECTED_MINIO_PORT = 9000
EXPECTED_MINIO_ACCESS_KEY_ID = "minioadmin"
EXPECTED_MINIO_SECRET_ACCESS_KEY = "minioadmin"
EXPECTED_MINIO_SIGNATURE_VERSION = "s3v4"
EXPECTED_MINIO_PHOTO_BUCKET_NAME = "profile-folder"
EXPECTED_MINIO_ACCESS_HOST = "http://localhost:9000"


def test_default_settings(settings=None):
    """Test default settings values."""
    settings = load_default_settings()

    assert settings.PROJECT_NAME == EXPECTED_PROJECT_NAME
    assert settings.API_V1_STR == EXPECTED_API_V1_STR
    assert settings.POSTGRES_HOST == EXPECTED_POSTGRES_HOST
    assert settings.POSTGRES_PORT == EXPECTED_POSTGRES_PORT
    assert settings.POSTGRES_USER == EXPECTED_POSTGRES_USER
    assert settings.POSTGRES_PASSWORD == EXPECTED_POSTGRES_PASSWORD
    assert settings.POSTGRES_DB == EXPECTED_POSTGRES_DB
    assert settings.SQLALCHEMY_POOL_SIZE == EXPECTED_SQLALCHEMY_POOL_SIZE
    assert settings.SQLALCHEMY_MAX_OVERFLOW == EXPECTED_SQLALCHEMY_MAX_OVERFLOW
    assert settings.TOKEN_SECRET_KEY == EXPECTED_TOKEN_SECRET_KEY
    assert settings.TOKEN_ALGORITHM == EXPECTED_TOKEN_ALGORITHM
    assert (
        settings.ACCESS_TOKEN_EXPIRE_MINUTES
        == EXPECTED_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    assert settings.PASS_ALGORITHM == EXPECTED_PASS_ALGORITHM
    assert settings.MINIO_SERVICE_NAME == EXPECTED_MINIO_SERVICE_NAME
    assert settings.MINIO_HOST == EXPECTED_MINIO_HOST
    assert settings.MINIO_PORT == EXPECTED_MINIO_PORT
    assert settings.MINIO_ACCESS_KEY_ID == EXPECTED_MINIO_ACCESS_KEY_ID
    assert settings.MINIO_SECRET_ACCESS_KEY == EXPECTED_MINIO_SECRET_ACCESS_KEY
    assert settings.MINIO_SIGNATURE_VERSION == EXPECTED_MINIO_SIGNATURE_VERSION
    assert settings.MINIO_PHOTO_BUCKET_NAME == EXPECTED_MINIO_PHOTO_BUCKET_NAME
    assert settings.MINIO_ACCESS_HOST == EXPECTED_MINIO_ACCESS_HOST


def test_assemble_db_url():
    """Test assembling the database URL from the settings."""
    settings = Settings(
        POSTGRES_USER="testuser",
        POSTGRES_PASSWORD="testpass",
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5432,
        POSTGRES_DB="testdb",
    )

    db_url = settings.SQLALCHEMY_DATABASE_URI
    assert isinstance(db_url, URL)
    assert db_url.drivername == "postgresql+asyncpg"
    assert db_url.username == "testuser"
    assert db_url.password == "testpass"
    assert db_url.host == "localhost"
    assert db_url.port == EXPECTED_POSTGRES_PORT
    assert db_url.database == "testdb"


def test_load_settings():
    """Test loading settings with caching."""
    settings1 = load_settings()
    settings2 = load_settings()

    assert settings1 is settings2
    assert isinstance(settings1, Settings)


def test_load_default_settings():
    """Test loading settings with caching."""
    settings1 = load_default_settings()
    settings2 = load_default_settings()

    assert settings1 is settings2
    assert isinstance(settings1, Settings)


def test_invalid_settings():
    """Test validation of invalid settings."""
    with pytest.raises(ValidationError):
        Settings(POSTGRES_PORT="invalid_port")  # type: ignore
