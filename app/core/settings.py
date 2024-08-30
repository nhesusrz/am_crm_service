"""Settings for the application."""

import functools
import typing
from pathlib import Path
from typing import Optional, Union

from pydantic import Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings
from sqlalchemy import engine
from sqlalchemy.engine import URL

# Base directory of the project, useful to load assets and configuration files
BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings."""

    # App Service
    PROJECT_NAME: str = "Customer Management API"
    API_V1_STR: str = "/api/v1"
    DEFAULT_ADMIN_USER: str = Field(
        validation_alias="DEFAULT_ADMIN_USER",
        default="admin",
    )
    DEFAULT_ADMIN_PASSWORD: str = Field(
        validation_alias="DEFAULT_ADMIN_PASSWORD",
        default="admin",
    )

    # Database settings
    POSTGRES_HOST: str = Field(
        validation_alias="POSTGRES_HOST",
        default="localhost",
    )
    POSTGRES_PORT: int = Field(validation_alias="POSTGRES_PORT", default=5432)
    POSTGRES_USER: str = Field(
        validation_alias="POSTGRES_USER",
        default="postgres",
    )
    POSTGRES_PASSWORD: str = Field(
        validation_alias="POSTGRES_PASSWORD",
        default="postgres",
    )
    POSTGRES_DB: str = Field(
        validation_alias="POSTGRES_DB",
        default="database_name",
    )

    SQLALCHEMY_POOL_SIZE: int = Field(
        validation_alias="SQLALCHEMY_POOL_SIZE",
        default=10,
    )
    SQLALCHEMY_MAX_OVERFLOW: int = Field(
        validation_alias="SQLALCHEMY_MAX_OVERFLOW",
        default=20,
    )

    # Computed property for the full database URI
    SQLALCHEMY_DATABASE_URI: Optional[Union[URL, str]] = None

    # Token generation
    TOKEN_SECRET_KEY: str = Field(
        validation_alias="TOKEN_SECRET_KEY",
        default="your_secret_key",
    )
    TOKEN_ALGORITHM: str = Field(
        validation_alias="TOKEN_ALGORITHM",
        default="HS256",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
        default=30,
    )

    # Password hashing
    PASS_ALGORITHM: str = Field(
        validation_alias="PASS_ALGORITHM",
        default="pbkdf2_sha256",
    )

    # MinIO Service
    MINIO_SERVICE_NAME: str = Field(
        validation_alias="MINIO_SERVICE_NAME",
        default="s3",
    )
    MINIO_HOST: str = Field(validation_alias="MINIO_HOST", default="localhost")
    MINIO_PORT: int = Field(validation_alias="MINIO_PORT", default=9000)
    MINIO_ACCESS_KEY_ID: str = Field(
        validation_alias="MINIO_ACCESS_KEY_ID",
        default="minioadmin",
    )
    MINIO_SECRET_ACCESS_KEY: str = Field(
        validation_alias="MINIO_SECRET_ACCESS_KEY",
        default="minioadmin",
    )
    MINIO_SIGNATURE_VERSION: str = Field(
        validation_alias="MINIO_SIGNATURE_VERSION",
        default="s3v4",
    )
    MINIO_PHOTO_BUCKET_NAME: str = Field(
        validation_alias="MINIO_PHOTO_BUCKET_NAME",
        default="profile-folder",
    )

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_url(
        cls,
        v: typing.Optional[str],
        values: FieldValidationInfo,
    ) -> typing.Union[engine.URL, str]:
        """Assemble DB connection.

        Args:
        ----
            v: Value of DB connection.
            values: FieldValidationInfo class with config values.

        Returns:
        -------
            DB connection.

        """
        if isinstance(v, str):
            return v
        return engine.URL.create(
            "postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_HOST"),
            port=values.data.get("POSTGRES_PORT"),
            database=values.data.get("POSTGRES_DB"),
        )

    class Config:
        """Pydantic settings configuration."""

        case_sensitive = True
        extra = "allow"
        env_file = ".env"  # Default to no file


@functools.lru_cache(maxsize=1)
def load_settings() -> Settings:
    """Load settings with caching to avoid computation."""
    return Settings()


@functools.lru_cache(maxsize=1)
def load_default_settings() -> Settings:
    """Get default settings values without loading .env."""

    class NoEnvSettings(Settings):
        class Config:  # type: ignore
            env_file = None

    return NoEnvSettings()
