"""Login endpoints tests."""

import pytest
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.v1.auth.login.login_endpoints import (
    ADMIN_LOGIN_ENDPOINT,
    REFRESH_TOKEN_ENDPOINT,
    USER_LOGIN_ENDPOINT,
)
from app.api.v1.auth.login.login_models import RefreshTokenRequest


@pytest.mark.asyncio
async def test_admin_login_success(mocker, async_client):
    """Test successful admin login by mocking the response.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.AsyncClient): Async HTTP client fixture.

    """
    mock_response = {
        "access_token": "mock_access_token",
        "token_type": "bearer",
    }

    mocker.patch(
        "httpx.AsyncClient.post",
        return_value=mocker.MagicMock(
            status_code=status.HTTP_200_OK,
            json=mocker.MagicMock(return_value=mock_response),
        ),
    )

    form_data = OAuth2PasswordRequestForm(
        username="admin",
        password="password",
    )
    data = {"username": form_data.username, "password": form_data.password}

    response = await async_client.post(url=ADMIN_LOGIN_ENDPOINT, data=data)

    assert response.status_code == status.HTTP_200_OK
    token_response = response.json()
    assert token_response["access_token"] == "mock_access_token"
    assert token_response["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_admin_login_failure(mocker, async_client):
    """Test admin login failure by mocking a 401 error response.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.AsyncClient): Async HTTP client fixture.

    """
    mocker.patch(
        "httpx.AsyncClient.post",
        return_value=mocker.MagicMock(
            status_code=status.HTTP_401_UNAUTHORIZED,
            json=mocker.MagicMock(
                return_value={"detail": "Invalid credentials"},
            ),
        ),
    )

    form_data = OAuth2PasswordRequestForm(
        username="wrong_admin",
        password="wrong_password",
    )
    data = {"username": form_data.username, "password": form_data.password}

    response = await async_client.post(url=ADMIN_LOGIN_ENDPOINT, data=data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error_response = response.json()
    assert error_response["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_user_login_success(mocker, async_client):
    """Test successful user login by mocking the response.


    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.AsyncClient): Async HTTP client fixture.

    """
    mock_response = {
        "access_token": "mock_access_token",
        "token_type": "bearer",
    }

    mocker.patch(
        "httpx.AsyncClient.post",
        return_value=mocker.MagicMock(
            status_code=status.HTTP_200_OK,
            json=mocker.MagicMock(return_value=mock_response),
        ),
    )

    form_data = OAuth2PasswordRequestForm(username="user", password="password")
    data = {"username": form_data.username, "password": form_data.password}

    response = await async_client.post(url=USER_LOGIN_ENDPOINT, data=data)

    assert response.status_code == status.HTTP_200_OK
    token_response = response.json()
    assert token_response["access_token"] == "mock_access_token"
    assert token_response["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_user_login_failure(mocker, async_client):
    """Test user login failure by mocking a 401 error response.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.AsyncClient): Async HTTP client fixture.

    """
    mocker.patch(
        "httpx.AsyncClient.post",
        return_value=mocker.MagicMock(
            status_code=status.HTTP_401_UNAUTHORIZED,
            json=mocker.MagicMock(
                return_value={"detail": "Invalid credentials"},
            ),
        ),
    )

    form_data = OAuth2PasswordRequestForm(
        username="wrong_user",
        password="wrong_password",
    )
    data = {"username": form_data.username, "password": form_data.password}

    response = await async_client.post(url=USER_LOGIN_ENDPOINT, data=data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error_response = response.json()
    assert error_response["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_refresh_token_success(mocker, async_client):
    """Test successful refresh token.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.AsyncClient): Async HTTP client fixture.

    """
    mock_response = {
        "access_token": "mock_access_token",
        "token_type": "bearer",
    }

    mocker.patch(
        "httpx.AsyncClient.post",
        return_value=mocker.MagicMock(
            status_code=status.HTTP_200_OK,
            json=mocker.MagicMock(return_value=mock_response),
        ),
    )

    refresh_token_request = RefreshTokenRequest(
        refresh_token="valid_refresh_token",
    )
    response = await async_client.post(
        url=REFRESH_TOKEN_ENDPOINT,
        json=refresh_token_request.dict(),
    )

    assert response.status_code == status.HTTP_200_OK
    token_response = response.json()
    assert token_response["access_token"] == "mock_access_token"
    assert token_response["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_failure(mocker, async_client):
    """Test refresh token failure by mocking a 401 error response.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.AsyncClient): Async HTTP client fixture.

    """
    mocker.patch(
        "httpx.AsyncClient.post",
        return_value=mocker.MagicMock(
            status_code=401,
            json=mocker.MagicMock(
                return_value={"detail": "Invalid refresh token"},
            ),
        ),
    )

    refresh_token_request = RefreshTokenRequest(
        refresh_token="invalid_refresh_token",
    )
    response = await async_client.post(
        url=REFRESH_TOKEN_ENDPOINT,
        json=refresh_token_request.dict(),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error_response = response.json()
    assert error_response["detail"] == "Invalid refresh token"
