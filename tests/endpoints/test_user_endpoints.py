"""User endpoints tests."""

import pytest
from fastapi import status
from httpx import AsyncClient

from app.api.v1.users.user_endpoints import USER_DETAIL_ENDPOINT, USER_ENDPOINT
from app.core.security import hash_password
from app.db.models.user_model import User
from app.schemas import user_schemas


@pytest.mark.asyncio
async def test_list_users_success(
    mocker,
    authenticated_admin_client: AsyncClient,
):
    """Test listing all users successfully.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture for mocking
        functions.
        authenticated_admin_client (AsyncClient): Async HTTP client fixture
        with admin authentication.

    """
    db_user_1 = User(id=1, username="user1", is_admin=False)
    db_user_2 = User(id=2, username="user2", is_admin=False)
    mocked_db_user_list = [db_user_1, db_user_2]
    mocker.patch(
        "app.db.actions.user_crud.get_all_users",
        return_value=mocked_db_user_list,
    )

    response = await authenticated_admin_client.get(USER_ENDPOINT)

    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert len(users) == len(mocked_db_user_list)
    assert users[0]["id"] == db_user_1.id
    assert users[0]["username"] == db_user_1.username
    assert users[0]["is_admin"] == db_user_1.is_admin
    assert users[1]["id"] == db_user_2.id
    assert users[1]["username"] == db_user_2.username
    assert users[1]["is_admin"] == db_user_2.is_admin


@pytest.mark.asyncio
async def test_list_users_empty(
    mocker,
    authenticated_admin_client: AsyncClient,
):
    """Test listing users when there are no users in the database.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture for mocking
        functions.
        authenticated_admin_client (AsyncClient): Async HTTP client fixture
        with admin authentication.

    """
    mocker.patch("app.db.actions.user_crud.get_all_users", return_value=[])

    response = await authenticated_admin_client.get(url=USER_ENDPOINT)

    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert len(users) == 0


@pytest.mark.asyncio
async def test_get_user_success(
    mocker,
    authenticated_admin_client: AsyncClient,
):
    """Test retrieving a specific user by ID successfully.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture for mocking
        functions.
        authenticated_admin_client (AsyncClient): Async HTTP client fixture
        with admin authentication.

    """
    mock_user = User(id=1, username="user1", is_admin=False)
    mocker.patch("app.db.actions.user_crud.get_user", return_value=mock_user)

    response = await authenticated_admin_client.get(
        url=USER_DETAIL_ENDPOINT.format(user_id=1),
    )

    assert response.status_code == status.HTTP_200_OK
    user = response.json()
    assert user["id"] == mock_user.id
    assert user["username"] == mock_user.username
    assert user["is_admin"] == mock_user.is_admin


@pytest.mark.asyncio
async def test_get_user_failure(
    mocker,
    authenticated_admin_client: AsyncClient,
):
    """Test retrieving a specific user by ID when the user does not exist.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture for mocking
        functions.
        authenticated_admin_client (AsyncClient): Async HTTP client fixture
        with admin authentication.

    """
    mocker.patch("app.db.actions.user_crud.get_user", return_value=None)

    response = await authenticated_admin_client.get(
        url=USER_DETAIL_ENDPOINT.format(user_id=1),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_create_user(mocker, authenticated_admin_client: AsyncClient):
    """Test creating a new user successfully.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture for mocking
        functions.
        authenticated_admin_client (AsyncClient): Async HTTP client fixture
        with admin authentication.

    """
    user_create_payload = user_schemas.UserCreate(
        username="new user",
        password="pass",
        is_admin=False,
    )

    db_user = User(
        id=1,
        username=user_create_payload.username,
        is_admin=user_create_payload.is_admin,
        hashed_password=hash_password(user_create_payload.password),
    )
    mocker.patch("app.db.actions.user_crud.create_user", return_value=db_user)

    response = await authenticated_admin_client.post(
        url=USER_ENDPOINT,
        json=user_create_payload.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    response_user = response.json()
    assert response_user["id"] == db_user.id
    assert response_user["username"] == db_user.username
    assert response_user["is_admin"] == db_user.is_admin


@pytest.mark.asyncio
async def test_delete_user_success(
    mocker,
    authenticated_admin_client: AsyncClient,
):
    """Test deleting a user by ID successfully.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture for mocking
        functions.
        authenticated_admin_client (AsyncClient): Async HTTP client fixture
        with admin authentication.

    """
    db_user = User(id=1, username="user1", is_admin=False)
    mocker.patch("app.db.actions.user_crud.get_user", return_value=db_user)
    mocker.patch("app.db.actions.user_crud.delete_user", return_value=None)

    response = await authenticated_admin_client.delete(
        url=USER_DETAIL_ENDPOINT.format(user_id=1),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "User deleted"}


@pytest.mark.asyncio
async def test_delete_user_failure(
    mocker,
    authenticated_admin_client: AsyncClient,
):
    """Test deleting a user by ID when the user does not exist.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture for mocking
        functions.
        authenticated_admin_client (AsyncClient): Async HTTP client fixture
        with admin authentication.

    """
    mocker.patch("app.db.actions.user_crud.get_user", return_value=None)

    response = await authenticated_admin_client.delete(
        url=USER_DETAIL_ENDPOINT.format(user_id=1),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_update_user_success(
    mocker,
    authenticated_admin_client: AsyncClient,
):
    """Test updating a user by ID successfully.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture for mocking
        functions.
        authenticated_admin_client (AsyncClient): Async HTTP client fixture
        with admin authentication.

    """
    db_user = User(
        id=1,
        username="user1",
        is_admin=False,
        hashed_password=hash_password("password"),
    )
    mocker.patch("app.db.actions.user_crud.get_user", return_value=db_user)

    db_user_updated = User(
        id=1,
        username="user1_new",
        is_admin=True,
        hashed_password=hash_password("new password"),
    )
    mocker.patch(
        "app.db.actions.user_crud.update_user",
        return_value=db_user_updated,
    )

    user_update_payload = user_schemas.UserUpdate(
        username=db_user_updated.username,
        password="new password",
        is_admin=db_user_updated.is_admin,
    )

    response = await authenticated_admin_client.put(
        url=USER_DETAIL_ENDPOINT.format(user_id=1),
        json=user_update_payload.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    response_user = response.json()
    assert response_user["id"] == db_user_updated.id
    assert response_user["username"] == db_user_updated.username
    assert response_user["is_admin"] == db_user_updated.is_admin


@pytest.mark.asyncio
async def test_update_user_failure(
    mocker,
    authenticated_admin_client: AsyncClient,
):
    """Test updating a user by ID when the user does not exist.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture for mocking
        functions.
        authenticated_admin_client (AsyncClient): Async HTTP client fixture
        with admin authentication.

    """
    mocker.patch("app.db.actions.user_crud.get_user", return_value=None)

    payload = {
        "username": "new name",
        "password": "new password",
        "is_admin": True,
    }

    response = await authenticated_admin_client.put(
        url=USER_DETAIL_ENDPOINT.format(user_id=1),
        json=payload,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}
