"""Conftest file for Pytest module."""

from unittest.mock import patch

import pytest
from fastapi import FastAPI, status
from fastapi.security import OAuth2PasswordRequestForm
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.v1.auth.login.login_endpoints import (
    ADMIN_LOGIN_ENDPOINT,
    USER_LOGIN_ENDPOINT,
    LoginEndpoints,
)
from app.api.v1.customers.customer_endpoints import CustomerEndpoints
from app.api.v1.users.user_endpoints import UserEndpoints
from app.db import base
from app.db.actions.user_crud import get_current_active_user
from app.db.base import Base
from app.db.models.user_model import User
from app.services.storage_service import S3Client
from tests.core.test_security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    TOKEN_ALGORITHM,
    TOKEN_SECRET_KEY,
)
from tests.db.models.test_customer_model import DATABASE_URL

app = FastAPI()
login_endpoints = LoginEndpoints()
user_endpoints = UserEndpoints()
customer_endpoints = CustomerEndpoints()
app.include_router(login_endpoints.get_router())
app.include_router(user_endpoints.get_router())
app.include_router(customer_endpoints.get_router())


async def mocked_get_current_active_user():
    """Mock function to simulate retrieving the current active user.

    Returns
    -------
        User: A `User` object representing a mocked active user with ID 123,
        username "admin", and `is_admin` set to `False`.

    """
    return User(id=123, username="admin", is_admin=False)


app.dependency_overrides[get_current_active_user] = (
    mocked_get_current_active_user
)


@pytest.fixture
async def async_client() -> AsyncClient:  # type: ignore
    """Fixture for creating an asynchronous HTTP client for testing.

    Yields
    ------
        AsyncClient: An async HTTP client configured for the FastAPI app.

    """
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client  # type: ignore


@pytest.fixture
async def authenticated_user_client(
    mocker,
    async_client: AsyncClient,
) -> AsyncClient:  # type: ignore
    """Fixture for creating an authenticated HTTP client for a regular user.

    Args:
    ----
        mocker (MockFixture): Pytest mock fixture.
        async_client (AsyncClient): An async HTTP client.

    Yields:
    ------
        AsyncClient: An authenticated async HTTP client with user token.

    """
    mock_user = User(id=123, username="user", is_admin=False)
    mocker.patch(
        "app.db.actions.user_crud.get_current_active_user",
        return_value=mock_user,
    )

    token_mock_response = {
        "access_token": "mock_access_token",
        "token_type": "bearer",
    }

    original_post = AsyncClient.post

    async def mock_post(url, *args, **kwargs):
        if url == USER_LOGIN_ENDPOINT:
            return mocker.MagicMock(
                status_code=status.HTTP_200_OK,
                json=mocker.MagicMock(return_value=token_mock_response),
            )
        return await original_post(
            self=async_client,
            url=url,
            *args,  # noqa
            **kwargs,
        )

    mocker.patch("httpx.AsyncClient.post", side_effect=mock_post)

    form_data = OAuth2PasswordRequestForm(username="user", password="password")
    data = {"username": form_data.username, "password": form_data.password}
    token_response = await async_client.post(USER_LOGIN_ENDPOINT, data=data)
    access_token = token_response.json()["access_token"]

    async_client.headers.update({"Authorization": f"Bearer {access_token}"})

    yield async_client  # type: ignore


@pytest.fixture
async def authenticated_admin_client(
    mocker,
    async_client: AsyncClient,
) -> AsyncClient:  # type: ignore
    """Fixture for creating an authenticated HTTP client for an admin user.

    Args:
    ----
        mocker (MockFixture): Pytest mock fixture.
        async_client (AsyncClient): An async HTTP client.

    Yields:
    ------
        AsyncClient: An authenticated async HTTP client with admin token.

    """
    token_mock_response = {
        "access_token": "mock_access_token",
        "token_type": "bearer",
    }

    original_post = AsyncClient.post

    async def mock_post(url, *args, **kwargs):
        if url == ADMIN_LOGIN_ENDPOINT:
            return mocker.MagicMock(
                status_code=status.HTTP_200_OK,
                json=mocker.MagicMock(return_value=token_mock_response),
            )
        return await original_post(
            self=async_client,
            url=url,
            *args,  # noqa
            **kwargs,
        )

    mocker.patch("httpx.AsyncClient.post", side_effect=mock_post)

    form_data = OAuth2PasswordRequestForm(
        username="admin",
        password="password",
    )
    data = {"username": form_data.username, "password": form_data.password}
    token_response = await async_client.post(ADMIN_LOGIN_ENDPOINT, data=data)
    access_token = token_response.json()["access_token"]

    async_client.headers.update({"Authorization": f"Bearer {access_token}"})

    yield async_client  # type: ignore


@pytest.fixture
def mock_app_settings():
    """Mock settings for testing security functions.

    Yields
    ------
        mock: The patched mock object with test settings.

    """
    with patch("app.core.security.app_settings") as mock:
        mock.TOKEN_SECRET_KEY = TOKEN_SECRET_KEY
        mock.TOKEN_ALGORITHM = TOKEN_ALGORITHM
        mock.ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
        yield mock


@pytest.fixture(scope="function")
async def async_db_session():
    """Fixture for creating and tearing down an asynchronous database session.

    Yields
    ------
        AsyncSession: An async SQLAlchemy session for database operations.

    """
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with engine.begin() as conn:
        await conn.run_sync(base.Base.metadata.create_all)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture(scope="function")
async def create_user(async_db_session):
    """Fixture for creating a test user in the database.

    Args:
    ----
        async_db_session (AsyncSession): An async SQLAlchemy session.

    Yields:
    ------
        User: The created test user.

    """
    new_user = User(
        username="testuser",
        hashed_password="hashed_password",
        is_admin=True,
    )
    async_db_session.add(new_user)
    await async_db_session.commit()
    await async_db_session.refresh(new_user)
    return new_user


@pytest.fixture(scope="module")
def engine():
    """Fixture that creates a new SQLAlchemy engine connected.

    Returns
    -------
        Engine: The SQLAlchemy engine instance connected to an in-memory
        SQLite database.

    """
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="module")
def setup_database(engine):
    """Fixture that sets up the database schema and tears it down after tests.

    Args:
    ----
        engine (Engine): The SQLAlchemy engine used for creating and dropping
        tables.

    Yields:
    ------
        None: This fixture sets up and tears down the database schema.

    """
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def s3_client():
    """Fixture that creates an instance of the S3Client singleton for testing.

    Returns
    -------
        S3Client: The S3Client singleton instance.

    """
    return S3Client()
