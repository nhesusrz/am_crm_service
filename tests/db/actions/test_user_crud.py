"""User CRUD tests."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from mock_alchemy.mocking import AlchemyMagicMock
from sqlalchemy.exc import SQLAlchemyError
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
USER_ID_1 = 1
USERNAME_1 = "john_doe"
PASSWORD = "password"
HASHED_PASSWORD = "hashed_password"
IS_ADMIN = True
UPDATED_USERNAME = "jane_doe"
UPDATED_PASSWORD = "new_password"
UPDATED_IS_ADMIN = False

USER_ID_2 = 2
USERNAME_2 = "john_doe #2"


@pytest.mark.asyncio
async def test_get_all_users():
    """Test retrieving all users from the database."""
    expected_len = 2
    mock_db_session = AsyncMock()
    mock_result = AlchemyMagicMock()
    mock_result.unique.return_value.scalars.return_value.all.return_value = [
        User(
            id=USER_ID_1,
            username=USERNAME_1,
            hashed_password=HASHED_PASSWORD,
            is_admin=IS_ADMIN,
        ),
        User(
            id=USER_ID_2,
            username=USERNAME_2,
            hashed_password=HASHED_PASSWORD,
            is_admin=IS_ADMIN,
        ),
    ]
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    users = await get_all_users(db_session=mock_db_session)

    assert len(users) == expected_len
    assert users[0].username == USERNAME_1
    assert users[1].username == USERNAME_2


@pytest.mark.asyncio
async def test_get_all_users_empty():
    """Test retrieving an emtpy list of users from the database."""
    mock_db_session = AsyncMock()
    mock_result = AlchemyMagicMock()
    mock_result.unique.return_value.scalars.return_value.all.return_value = []
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    users = await get_all_users(db_session=mock_db_session)

    assert len(users) == 0


@pytest.mark.asyncio
async def test_get_user():
    """Test retrieving a specific user by ID."""
    mock_db_session = AsyncMock()
    mock_result = AlchemyMagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=USER_ID_1,
        username=USERNAME_1,
        hashed_password=HASHED_PASSWORD,
        is_admin=IS_ADMIN,
    )
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    user = await get_user(db_session=mock_db_session, user_id=USER_ID_1)

    assert user is not None
    assert user.id == USER_ID_1
    assert user.username == USERNAME_1


@pytest.mark.asyncio
async def test_get_non_existing_user():
    """Test retrieving a specific user by wrong ID."""
    mock_db_session = AsyncMock()
    mock_result = AlchemyMagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    user = await get_user(db_session=mock_db_session, user_id=USER_ID_1)

    assert user is None


@pytest.mark.asyncio
async def test_create_user_success():
    """Test creating a new user."""
    mock_db_session = AsyncMock()
    mock_db_session.add = AsyncMock()
    mock_db_session.commit = AsyncMock()

    user_create_request = UserCreate(
        username=USERNAME_1,
        password=PASSWORD,
        is_admin=IS_ADMIN,
    )

    with patch(
        "app.db.actions.user_crud.hash_password",
        return_value=HASHED_PASSWORD,
    ):
        created_user = await create_user(
            db_session=mock_db_session,
            user=user_create_request,
        )

    assert created_user is not None
    assert created_user.username == USERNAME_1
    assert created_user.hashed_password == HASHED_PASSWORD
    assert created_user.is_admin == IS_ADMIN


@pytest.mark.asyncio
async def test_create_user_failure():
    """Test creating a new user but without success."""
    mock_db_session = AsyncMock()
    mock_db_session.add = AsyncMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.commit.side_effect = SQLAlchemyError("Database error")

    user_create_request = UserCreate(
        username=USERNAME_1,
        password=PASSWORD,
        is_admin=IS_ADMIN,
    )

    patch(
        "app.db.actions.user_crud.hash_password",
        return_value=HASHED_PASSWORD,
    )
    with pytest.raises(SQLAlchemyError):
        await create_user(
            db_session=mock_db_session,
            user=user_create_request,
        )

    mock_db_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_user_success():
    """Test deleting a user successfully."""
    mock_db_session = AsyncMock()
    mock_db_session.delete = AsyncMock()
    mock_db_session.commit = AsyncMock()

    user = User(
        id=USER_ID_1,
        username=USERNAME_1,
        hashed_password=HASHED_PASSWORD,
        is_admin=IS_ADMIN,
    )

    await delete_user(db_session=mock_db_session, user=user)

    mock_db_session.delete.assert_called_once_with(user)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user_failure():
    """Test deleting a user without success."""
    mock_db_session = AsyncMock()
    mock_db_session.delete = AsyncMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.commit.side_effect = SQLAlchemyError("Database error")

    user = User(
        id=USER_ID_1,
        username=USERNAME_1,
        hashed_password=HASHED_PASSWORD,
        is_admin=IS_ADMIN,
    )

    with pytest.raises(SQLAlchemyError):
        await delete_user(db_session=mock_db_session, user=user)

        mock_db_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_user_success():
    """Test updating an existing user successfully."""
    mock_db_session = AsyncMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock()

    existing_user = User(
        id=USER_ID_1,
        username=USERNAME_1,
        hashed_password=HASHED_PASSWORD,
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
            db_session=mock_db_session,
            db_user=existing_user,
            user_request=user_update,
        )

    assert updated_user is not None
    assert updated_user.username == UPDATED_USERNAME
    assert updated_user.hashed_password == "new_hashed_password"
    assert updated_user.is_admin == UPDATED_IS_ADMIN


@pytest.mark.asyncio
async def test_update_user_failure():
    """Test updating an existing user without success."""
    mock_db_session = AsyncMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock()
    mock_db_session.commit.side_effect = SQLAlchemyError("Database error")

    existing_user = User(
        id=USER_ID_1,
        username=USERNAME_1,
        hashed_password=HASHED_PASSWORD,
        is_admin=IS_ADMIN,
    )

    user_update = UserUpdate(
        username=UPDATED_USERNAME,
        password=UPDATED_PASSWORD,
        is_admin=UPDATED_IS_ADMIN,
    )

    patch(
        "app.db.actions.user_crud.hash_password",
        return_value="new_hashed_password",
    )
    with pytest.raises(SQLAlchemyError):
        await update_user(
            db_session=mock_db_session,
            db_user=existing_user,
            user_request=user_update,
        )

        mock_db_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_current_active_user_admin_success():
    """Test retrieving the current valid active admin user."""
    mock_db_session = AsyncMock()
    mock_user = User(
        id=USER_ID_1,
        username=USERNAME_1,
        hashed_password=HASHED_PASSWORD,
        is_admin=IS_ADMIN,
    )

    with patch(
        "app.db.actions.user_crud.verify_token",
        return_value=USER_ID_1,
    ):
        mock_result = AlchemyMagicMock()
        mock_scalars = mock_result.unique.return_value.scalars
        mock_first = mock_scalars.return_value.first
        mock_first.return_value = mock_user

        mock_db_session.execute = AsyncMock(return_value=mock_result)

        active_user = await get_current_active_user(
            token="valid_token",
            db_session=mock_db_session,
            is_admin=True,
        )

    assert active_user is not None
    assert active_user.id == USER_ID_1
    assert active_user.username == USERNAME_1
    assert active_user.is_admin == IS_ADMIN


@pytest.mark.asyncio
async def test_get_current_active_user_not_admin():
    """Test retrieving the current not valid active admin user."""
    mock_db_session = AsyncMock()
    mock_user = User(
        id=USER_ID_1,
        username=USERNAME_1,
        hashed_password=HASHED_PASSWORD,
        is_admin=False,
    )

    with patch(
        "app.db.actions.user_crud.verify_token",
        return_value=USER_ID_1,
    ):
        mock_result = AlchemyMagicMock()
        mock_scalars = mock_result.unique.return_value.scalars
        mock_first = mock_scalars.return_value.first
        mock_first.return_value = mock_user

        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(
                token="valid_token",
                db_session=mock_db_session,
                is_admin=True,
            )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Not enough permissions"


@pytest.mark.asyncio
async def test_get_current_active_user_invalid_token():
    """Test handling an invalid OAuth2 token."""
    mock_db_session = AsyncMock()

    patch("app.core.security.verify_token", return_value=None)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(
            token="invalid_token",
            db_session=mock_db_session,
            is_admin=True,
        )

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token"


@pytest.mark.asyncio
async def test_get_current_active_user_not_found():
    """Test handling a user when the user is not found."""
    mock_db_session = AsyncMock()

    with patch("app.core.security.verify_token", return_value=USER_ID_1):
        mock_db_session.execute = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(
                token="valid_token",
                db_session=mock_db_session,
                is_admin=True,
            )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert exc_info.value.detail == "User not found"
