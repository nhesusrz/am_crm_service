"""Security tests."""

from datetime import timedelta
from unittest.mock import AsyncMock

import pytest
from jose import jwt
from mock_alchemy.mocking import AlchemyMagicMock

from app.core.security import (
    authenticate_user,
    create_access_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.db.models.user_model import User

USER_ID = 1
EXPIRES_DELTA = timedelta(minutes=30)
TOKEN_SECRET_KEY = "test_secret_key"
TOKEN_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
USERNAME = "testuser"
PASSWORD = "testpassword"
HASHED_PASSWORD = hash_password(PASSWORD)
INVALID_TOKEN = "invalid_token"


@pytest.mark.asyncio
async def test_create_access_token(mock_app_settings):  # noqa
    """Test creating an access token with a valid user ID and expiration time.

    Args:
    ----
        mock_settings (MagicMock): Mocked settings fixture.

    """
    token = await create_access_token(USER_ID, expires_delta=EXPIRES_DELTA)

    assert token is not None
    assert isinstance(token, str)

    payload = jwt.decode(
        token,
        mock_app_settings.TOKEN_SECRET_KEY,
        algorithms=[mock_app_settings.TOKEN_ALGORITHM],
    )
    assert payload.get("id") == USER_ID


@pytest.mark.asyncio
async def test_verify_token_success(mock_app_settings):  # noqa
    """Test verifying a valid token.

    Args:
    ----
        mock_settings (MagicMock): Mocked settings fixture.

    """
    token = await create_access_token(USER_ID)
    user_id = await verify_token(token)

    assert user_id == USER_ID


@pytest.mark.asyncio
async def test_verify_token_invalid_token(mock_app_settings):  # noqa
    """Test verifying an invalid token raises an HTTPException.

    Args:
    ----
        mock_settings (MagicMock): Mocked settings fixture.

    """
    user_id = await verify_token(INVALID_TOKEN)
    assert not user_id


def test_hash_password():
    """Test hashing a password."""
    hashed = hash_password(PASSWORD)

    assert hashed is not None
    assert verify_password(PASSWORD, hashed)


def test_verify_password_success():
    """Test verifying a password against a hashed password."""
    result = verify_password(PASSWORD, HASHED_PASSWORD)

    assert result is True


def test_verify_password_failure():
    """Test verifying a password against a hashed password with incorrect.

    password.
    """
    result = verify_password("wrongpassword", HASHED_PASSWORD)

    assert result is False


@pytest.mark.asyncio
async def test_authenticate_user_success(mocker):
    """Test authenticating a user successfully.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture for mocking.

    """
    mock_db_user = User(
        id=USER_ID,
        username=USERNAME,
        hashed_password=HASHED_PASSWORD,
        is_admin=False,
    )

    mock_result = AlchemyMagicMock()
    mock_result.unique.return_value.scalars.return_value.first.return_value = (
        mock_db_user
    )

    mock_db_session = AsyncMock()
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    mocker.patch("app.core.security.verify_password", return_value=True)

    user = await authenticate_user(mock_db_session, USERNAME, PASSWORD)

    assert user is not None
    assert user.username == USERNAME
    assert user.hashed_password == HASHED_PASSWORD
    assert not user.is_admin


@pytest.mark.asyncio
async def test_authenticate_user_failure(mocker):
    """Test authenticating a user with incorrect credentials.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture for mocking.

    """
    mock_db_user = User(
        id=USER_ID,
        username=USERNAME,
        hashed_password=HASHED_PASSWORD,
        is_admin=False,
    )

    mock_result = AlchemyMagicMock()
    mock_result.unique.return_value.scalars.return_value.first.return_value = (
        mock_db_user
    )

    mock_db_session = AsyncMock()
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    mocker.patch("app.core.security.verify_password", return_value=False)

    user = await authenticate_user(mock_db_session, USERNAME, PASSWORD)

    assert user is None
