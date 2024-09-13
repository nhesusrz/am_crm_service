"""Login endpoints tests."""

import pytest
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError

from app.api.v1.auth.login.login_endpoints import (
    ADMIN_LOGIN_ENDPOINT,
    REFRESH_TOKEN_ENDPOINT,
    USER_LOGIN_ENDPOINT,
    LoginEndpoints,
)
from app.api.v1.auth.login.login_models import (
    RefreshTokenRequest,
    TokenResponseModel,
)
from app.db.models.user_model import User


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
async def test_admin_login_authenticate_user_success(mocker, async_client):
    """Test successful admin login.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.AsyncClient): Async HTTP client fixture.

    """
    form_data = OAuth2PasswordRequestForm(
        username="admin",
        password="password",
    )
    data = {"username": form_data.username, "password": form_data.password}
    mocker.patch(
        "app.core.security.authenticate_user",
        return_value=1,
    )
    mock_token_resp_model = TokenResponseModel(
        access_token="mock_access_token",
        token_type="bearer",
    )
    mocker.patch(
        "app.api.v1.auth.login.login_endpoints"
        ".LoginEndpoints._generate_token_response_model",
        return_value=mock_token_resp_model,
    )

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
async def test_admin_login_authenticate_user_failure(mocker, async_client):
    """Test admin login failure by mocking security.authenticate_user.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.Asyn cClient): Async HTTP client fixture.

    """
    form_data = OAuth2PasswordRequestForm(
        username="admin",
        password="password",
    )
    data = {"username": form_data.username, "password": form_data.password}

    mocker.patch(
        "app.core.security.authenticate_user",
        return_value=None,
    )

    response = await async_client.post(url=ADMIN_LOGIN_ENDPOINT, data=data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Invalid credentials",
    }


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
async def test_user_login_authenticate_user_success(mocker, async_client):
    """Test successful user login.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.AsyncClient): Async HTTP client fixture.

    """
    form_data = OAuth2PasswordRequestForm(
        username="user",
        password="password",
    )
    data = {"username": form_data.username, "password": form_data.password}
    mocker.patch(
        "app.core.security.authenticate_user",
        return_value=1,
    )
    mock_token_resp_model = TokenResponseModel(
        access_token="mock_access_token",
        token_type="bearer",
    )
    mocker.patch(
        "app.api.v1.auth.login.login_endpoints"
        ".LoginEndpoints._generate_token_response_model",
        return_value=mock_token_resp_model,
    )

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
async def test_user_login_authenticate_user_failure(mocker, async_client):
    """Test user login failure by mocking security.authenticate_user.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.AsyncClient): Async HTTP client fixture.

    """
    form_data = OAuth2PasswordRequestForm(
        username="user",
        password="password",
    )
    data = {"username": form_data.username, "password": form_data.password}

    mocker.patch(
        "app.core.security.authenticate_user",
        return_value=None,
    )

    response = await async_client.post(url=USER_LOGIN_ENDPOINT, data=data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error_response = response.json()
    assert error_response["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_refresh_token_success(mocker, async_client):
    """Test successful refresh token by mocking the response.

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
        json=refresh_token_request.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    token_response = response.json()
    assert token_response["access_token"] == "mock_access_token"
    assert token_response["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_verify_token_success(mocker, async_client):
    """Test successful refresh token mocking security.verify_token.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.AsyncClient): Async HTTP client fixture.

    """
    refresh_token_request = RefreshTokenRequest(
        refresh_token="valid_refresh_token",
    )
    mocker.patch(
        "app.core.security.verify_token",
        return_value=1,
    )
    mocker.patch(
        "app.core.security.create_access_token",
        return_value="new_access_token",
    )

    response = await async_client.post(
        url=REFRESH_TOKEN_ENDPOINT,
        json=refresh_token_request.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    token_response = response.json()
    assert token_response["access_token"] == "new_access_token"
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
        json=refresh_token_request.model_dump(),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error_response = response.json()
    assert error_response["detail"] == "Invalid refresh token"


@pytest.mark.asyncio
async def test_refresh_token_verify_token_exception(mocker, async_client):
    """Test refresh token failure by mocking verify_token exception.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.AsyncClient): Async HTTP client fixture.

    """
    refresh_token_request = RefreshTokenRequest(
        refresh_token="valid_refresh_token",
    )
    mocker.patch(
        "app.core.security.verify_token",
        side_effect=JWTError("Some error occurred"),
    )

    response = await async_client.post(
        url=REFRESH_TOKEN_ENDPOINT,
        json=refresh_token_request.model_dump(),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error_response = response.json()
    assert error_response["detail"] == "Some error occurred"


@pytest.mark.asyncio
async def test_refresh_token_verify_token_none(mocker, async_client):
    """Test refresh token failure by mocking verify_token result None.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.AsyncClient): Async HTTP client fixture.

    """
    refresh_token_request = RefreshTokenRequest(
        refresh_token="valid_refresh_token",
    )
    mocker.patch(
        "app.core.security.verify_token",
        return_value=None,
    )

    response = await async_client.post(
        url=REFRESH_TOKEN_ENDPOINT,
        json=refresh_token_request.model_dump(),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error_response = response.json()
    assert error_response["detail"] == "401: Invalid refresh token"


@pytest.mark.asyncio
async def test_refresh_token_create_access_token_failure(mocker, async_client):
    """Test refresh token failure by mocking create_access_token exception.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.AsyncClient): Async HTTP client fixture.

    """
    refresh_token_request = RefreshTokenRequest(
        refresh_token="valid_refresh_token",
    )
    mocker.patch(
        "app.core.security.verify_token",
        return_value=1,
    )
    mocker.patch(
        "app.core.security.create_access_token",
        side_effect=JWTError("Encoding error occurred"),
    )

    response = await async_client.post(
        url=REFRESH_TOKEN_ENDPOINT,
        json=refresh_token_request.model_dump(),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error_response = response.json()
    assert error_response["detail"] == "Encoding error occurred"


@pytest.mark.asyncio
async def test__generate_token_response_model(mocker):
    """Test _generate_token_response_model.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        async_client (httpx.AsyncClient): Async HTTP client fixture.

    """
    user = User(
        id=1,
        username="username",
        hashed_password="hashed password",
        is_admin=True,
    )
    mocker.patch(
        "app.core.security.create_access_token",
        return_value="new token",
    )

    login_endpoint_instance = LoginEndpoints()
    token_response_model = (
        await (
            login_endpoint_instance._generate_token_response_model(
                db_user=user,
            )
        )
    )

    assert token_response_model.access_token == "new token"
    assert token_response_model.token_type == "bearer"
