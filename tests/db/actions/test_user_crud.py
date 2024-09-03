"""User CRUD tests."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from mock_alchemy.mocking import AlchemyMagicMock
from starlette import status

from app.db.actions.user_crud import (
    create_user,
    delete_user,
    get_all_users,
    get_current_active_user,
    get_user,
    update_user,
)
from app.db.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate

# Constants for testing
USER_ID = 1
USERNAME = "john_doe"
PASSWORD = "password"
HASHE_PASSWORD = "hashed_password"
IS_ADMIN = True
UPDATED_USERNAME = "jane_doe"
UPDATED_PASSWORD = "new_password"
UPDATED_IS_ADMIN = False


@pytest.mark.asyncio
async def test_get_all_users():
    """Test retrieving all users from the database."""
    mock_db_session = AsyncMock()
    mock_result = AlchemyMagicMock()
    mock_result.unique.return_value.scalars.return_value.all.return_value = [
        User(
            id=USER_ID,
            username=USERNAME,
            hashed_password=HASHE_PASSWORD,
            is_admin=IS_ADMIN,
        ),
    ]
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    users = await get_all_users(mock_db_session)

    assert len(users) == 1
    assert users[0].username == USERNAME


@pytest.mark.asyncio
async def test_get_user():
    """Test retrieving a specific user by ID."""
    mock_db_session = AsyncMock()
    mock_result = AlchemyMagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=USER_ID,
        username=USERNAME,
        hashed_password=HASHE_PASSWORD,
        is_admin=IS_ADMIN,
    )
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    user = await get_user(mock_db_session, USER_ID)

    assert user is not None
    assert user.id == USER_ID
    assert user.username == USERNAME


@pytest.mark.asyncio
async def test_create_user():
    """Test creating a new user."""
    mock_db_session = AsyncMock()
    mock_db_session.add = AsyncMock()
    mock_db_session.commit = AsyncMock()

    user_create_request = UserCreate(
        username=USERNAME,
        password=PASSWORD,
        is_admin=IS_ADMIN,
    )

    with patch(
        "app.db.actions.user_crud.hash_password",
        return_value=HASHE_PASSWORD,
    ):
        created_user = await create_user(mock_db_session, user_create_request)

    assert created_user is not None
    assert created_user.username == USERNAME
    assert created_user.hashed_password == HASHE_PASSWORD
    assert created_user.is_admin == IS_ADMIN


@pytest.mark.asyncio
async def test_delete_user():
    """Test deleting a user."""
    mock_db_session = AsyncMock()
    mock_db_session.delete = AsyncMock()
    mock_db_session.commit = AsyncMock()

    user = User(
        id=USER_ID,
        username=USERNAME,
        hashed_password=HASHE_PASSWORD,
        is_admin=IS_ADMIN,
    )

    await delete_user(mock_db_session, user)

    mock_db_session.delete.assert_called_once_with(user)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_user():
    """Test updating an existing user."""
    mock_db_session = AsyncMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock()

    existing_user = User(
        id=USER_ID,
        username=USERNAME,
        hashed_password=HASHE_PASSWORD,
        is_admin=IS_ADMIN,
    )

    user_update = UserUpdate(
        username=UPDATED_USERNAME,
        password=UPDATED_PASSWORD,
        is_admin=UPDATED_IS_ADMIN,
    )

    with patch(
        "app.db.actions.user_crud.hash_password",
        return_value="new_hashed_password",
    ):
        updated_user = await update_user(
            mock_db_session,
            existing_user,
            user_update,
        )

    assert updated_user is not None
    assert updated_user.username == UPDATED_USERNAME
    assert updated_user.hashed_password == "new_hashed_password"
    assert updated_user.is_admin == UPDATED_IS_ADMIN


@pytest.mark.asyncio
async def test_get_current_active_user():
    """Test retrieving the current active admin user."""
    mock_db_session = AsyncMock()
    token = "valid_token"
    user_id = USER_ID
    mock_user = User(
        id=USER_ID,
        username=USERNAME,
        hashed_password=HASHE_PASSWORD,
        is_admin=IS_ADMIN,
    )

    with patch("app.db.actions.user_crud.verify_token", return_value=user_id):
        mock_result = AlchemyMagicMock()
        mock_scalars = mock_result.unique.return_value.scalars
        mock_first = mock_scalars.return_value.first
        mock_first.return_value = mock_user

        mock_db_session.execute = AsyncMock(return_value=mock_result)

        active_user = await get_current_active_user(
            token,
            mock_db_session,
            is_admin=True,
        )

    assert active_user is not None
    assert active_user.id == USER_ID
    assert active_user.username == USERNAME


@pytest.mark.asyncio
async def test_get_current_active_user_invalid_token():
    """Test handling an invalid OAuth2 token."""
    mock_db_session = AsyncMock()
    invalid_token = "invalid_token"

    with patch("app.core.security.verify_token", return_value=None):
        try:
            await get_current_active_user(
                invalid_token,
                mock_db_session,
                is_admin=True,
            )
        except HTTPException as excinfo:
            assert excinfo.status_code == status.HTTP_401_UNAUTHORIZED
            assert excinfo.detail == "Invalid token"
        else:
            pytest.fail("Expected HTTPException was not raised")


@pytest.mark.asyncio
async def test_get_current_active_user_not_admin():
    """Test handling a non-admin user when admin access is required."""
    mock_db_session = AsyncMock()
    token = "valid_token"
    user_id = USER_ID
    non_admin_user = User(
        id=USER_ID,
        username=USERNAME,
        hashed_password=HASHE_PASSWORD,
        is_admin=False,
    )

    with patch("app.core.security.verify_token", return_value=user_id):
        mock_result = AsyncMock()
        mock_scalars = mock_result.unique.return_value.scalars
        mock_first = mock_scalars.return_value.first
        mock_first.return_value = non_admin_user

        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(HTTPException) as excinfo:
            await get_current_active_user(
                token,
                mock_db_session,
                is_admin=True,
            )

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Invalid token"
