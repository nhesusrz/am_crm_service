"""Customer endpoints tests."""

import pytest
from fastapi import status

from app.api.v1.customers.customer_endpoints import (
    CUSTOMER_DETAIL_ENDPOINT,
    CUSTOMER_ENDPOINT,
    CUSTOMER_UPLOAD_PHOTO_ENDPOINT,
)
from app.db.models.customer_model import Customer
from app.schemas.customer_schemas import CustomerBase


@pytest.mark.asyncio
async def test_list_customers(mocker, authenticated_user_client):
    """Test retrieving a list of all customers by mocking the response.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    db_customer_1 = Customer(
        id=1,
        name="Customer 1",
        surname="Customer 1",
        photo_url="http://photo1.jpg",
        creator_id=3,
        modifier_id=3,
    )
    db_customer_2 = Customer(
        id=2,
        name="Customer 2",
        surname="Customer 2",
        photo_url="http://photo2.jpg",
        creator_id=3,
        modifier_id=4,
    )
    user_count = 2
    mocked_db_customer_list = [db_customer_1, db_customer_2]
    mocker.patch(
        "app.db.actions.customer_crud.get_all_customers",
        return_value=mocked_db_customer_list,
    )

    response = await authenticated_user_client.get(url=CUSTOMER_ENDPOINT)

    assert response.status_code == status.HTTP_200_OK
    customers = response.json()
    assert len(customers) == user_count
    assert customers[0]["name"] == db_customer_1.name
    assert customers[0]["surname"] == db_customer_1.surname
    assert customers[0]["photo_url"] == db_customer_1.photo_url
    assert customers[0]["creator_id"] == db_customer_1.creator_id
    assert customers[0]["modifier_id"] == db_customer_1.modifier_id
    assert customers[1]["name"] == db_customer_2.name
    assert customers[1]["surname"] == db_customer_2.surname
    assert customers[1]["photo_url"] == db_customer_2.photo_url
    assert customers[1]["creator_id"] == db_customer_2.creator_id
    assert customers[1]["modifier_id"] == db_customer_2.modifier_id


@pytest.mark.asyncio
async def test_list_customers_empty(mocker, authenticated_user_client):
    """Test retrieving a list of all customers by mocking the response.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mocker.patch(
        "app.db.actions.customer_crud.get_all_customers",
        return_value=[],
    )

    response = await authenticated_user_client.get(url=CUSTOMER_ENDPOINT)

    assert response.status_code == status.HTTP_200_OK
    customers = response.json()
    assert len(customers) == 0


@pytest.mark.asyncio
async def test_get_customer_success(mocker, authenticated_user_client):
    """Test retrieving a customer by ID by mocking the response.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mocked_db_customer = Customer(
        id=1,
        name="Customer 1",
        surname="Customer 1",
        photo_url="http://photo1.jpg",
        creator_id=12,
        modifier_id=3,
    )

    mocker.patch(
        "app.db.actions.customer_crud.get_customer",
        return_value=mocked_db_customer,
    )

    response = await authenticated_user_client.get(
        url=CUSTOMER_DETAIL_ENDPOINT.format(customer_id=1),
    )

    assert response.status_code == status.HTTP_200_OK
    customer = response.json()
    assert customer["id"] == mocked_db_customer.id
    assert customer["name"] == mocked_db_customer.name


@pytest.mark.asyncio
async def test_get_customer_failure(mocker, authenticated_user_client):
    """Test retrieving a customer by ID by mocking the response.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mocker.patch(
        "app.db.actions.customer_crud.get_customer",
        return_value=None,
    )

    response = await authenticated_user_client.get(
        url=CUSTOMER_DETAIL_ENDPOINT.format(customer_id=1),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Customer not found"}


@pytest.mark.asyncio
async def test_create_customer_success(mocker, authenticated_user_client):
    """Test creating a new customer by mocking the response.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mocked_db_customer = Customer(
        id=1,
        name="Customer 1",
        surname="Customer 1",
        photo_url="http://photo1.jpg",
        creator_id=123,
        modifier_id=123,
    )
    mocker.patch(
        "app.db.actions.customer_crud.create_customer",
        return_value=mocked_db_customer,
    )

    payload = {
        "name": "Customer 1",
        "surname": "Customer 1",
        "photo_url": "http://photo1.jpg",
    }

    response = await authenticated_user_client.post(
        CUSTOMER_ENDPOINT,
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK
    customer = response.json()
    assert customer["name"] == mocked_db_customer.name
    assert customer["surname"] == mocked_db_customer.surname
    assert customer["photo_url"] == mocked_db_customer.photo_url


@pytest.mark.asyncio
async def test_delete_customer_success(mocker, authenticated_user_client):
    """Test deleting a customer by ID by mocking the response.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mocked_db_customer = Customer(
        id=1,
        name="Customer 1",
        surname="Customer 1",
        photo_url="http://photo1.jpg",
        creator_id=123,
        modifier_id=123,
    )
    mocker.patch(
        "app.db.actions.customer_crud.get_customer",
        return_value=mocked_db_customer,
    )
    mocker.patch("app.db.actions.customer_crud.delete_customer")

    response = await authenticated_user_client.delete(
        url=CUSTOMER_DETAIL_ENDPOINT.format(customer_id=1),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "Customer deleted"}


@pytest.mark.asyncio
async def test_delete_customer_failure(mocker, authenticated_user_client):
    """Test failing to delete a customer by ID by mocking an error response.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mocker.patch(
        "app.db.actions.customer_crud.get_customer",
        return_value=None,
    )

    response = await authenticated_user_client.delete(
        url=CUSTOMER_DETAIL_ENDPOINT.format(customer_id=1),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Customer not found"}


@pytest.mark.asyncio
async def test_update_customer_success(mocker, authenticated_user_client):
    """Test updating a customer by ID by mocking the response.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mocked_db_customer = Customer(
        id=1,
        name="Customer 1",
        surname="Customer 1",
        photo_url="http://photo1.jpg",
        creator_id=12,
        modifier_id=3,
    )
    mocked_db_customer_updated = Customer(
        id=1,
        name="Customer 1 Updated",
        surname="Customer 1 Updated",
        photo_url="http://photo1_updated.jpg",
        creator_id=12,
        modifier_id=123,
    )

    mocker.patch(
        "app.db.actions.customer_crud.get_customer",
        return_value=mocked_db_customer,
    )
    mocker.patch(
        "app.db.actions.customer_crud.update_customer",
        return_value=mocked_db_customer_updated,
    )

    payload = {
        "name": "Customer 1 Updated",
        "surname": "Customer 1 Updated",
        "photo_url": "http://photo1_updated.jpg",
    }

    response = await authenticated_user_client.put(
        url=CUSTOMER_DETAIL_ENDPOINT.format(customer_id=1),
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK
    customer = response.json()
    assert customer["name"] == mocked_db_customer_updated.name
    assert customer["surname"] == mocked_db_customer_updated.surname
    assert customer["photo_url"] == mocked_db_customer_updated.photo_url
    assert customer["creator_id"] == mocked_db_customer_updated.creator_id
    assert customer["modifier_id"] == mocked_db_customer_updated.modifier_id


@pytest.mark.asyncio
async def test_update_customer_failure_get_customer(
    mocker,
    authenticated_user_client,
):
    """Test failing to update a customer by ID by mocking get_customer.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mocker.patch(
        "app.db.actions.customer_crud.get_customer",
        return_value=None,
    )

    payload = {
        "name": "Customer 1 Updated",
        "surname": "Customer 1 Updated",
        "photo_url": "http://photo1_updated.jpg",
    }

    response = await authenticated_user_client.put(
        url=CUSTOMER_DETAIL_ENDPOINT.format(customer_id=1),
        json=payload,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Customer not found"}


@pytest.mark.asyncio
async def test_update_customer_failure_update_customer(
    mocker,
    authenticated_user_client,
):
    """Test failing to update a customer by ID by mocking update_customer.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mocked_db_customer = Customer(
        id=1,
        name="Customer 1",
        surname="Customer 1",
        photo_url="http://photo1.jpg",
        creator_id=12,
        modifier_id=3,
    )

    mocker.patch(
        "app.db.actions.customer_crud.get_customer",
        return_value=mocked_db_customer,
    )

    mocker.patch(
        "app.db.actions.customer_crud.update_customer",
        return_value=None,
    )

    payload = {
        "name": "Customer 1 Updated",
        "surname": "Customer 1 Updated",
        "photo_url": "http://photo1_updated.jpg",
    }

    response = await authenticated_user_client.put(
        url=CUSTOMER_DETAIL_ENDPOINT.format(customer_id=1),
        json=payload,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Customer update failed"}


@pytest.mark.asyncio
async def test_upload_photo_success(mocker, authenticated_user_client):
    """Test uploading a photo for a customer by mocking the response.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mock_photo_url = "http://example.com/photo_new.jpg"
    mock_upload_file = mocker.MagicMock()
    mock_upload_file.filename = "photo.jpg"
    mock_upload_file.read = b"photo content"
    mocker.patch(
        "app.services.storage_service.S3Client.upload_file",
        return_value=mock_photo_url,
    )

    mocked_db_customer = Customer(
        id=1,
        name="Customer 1",
        surname="Customer 1",
        photo_url=None,
        creator_id=12,
        modifier_id=3,
    )
    mocked_db_customer_updated = Customer(
        id=1,
        name="Customer 1",
        surname="Customer 1",
        photo_url=mock_photo_url,
        creator_id=12,
        modifier_id=123,
    )

    mocker.patch(
        "app.db.actions.customer_crud.get_customer",
        return_value=mocked_db_customer,
    )
    mocker.patch(
        "app.db.actions.customer_crud.update_customer",
        return_value=mocked_db_customer_updated,
    )

    response = await authenticated_user_client.put(
        url=CUSTOMER_UPLOAD_PHOTO_ENDPOINT.format(customer_id=1),
        files={"file": (mock_upload_file.filename, mock_upload_file.read)},
    )

    assert response.status_code == status.HTTP_200_OK
    customer = response.json()
    assert customer["name"] == mocked_db_customer_updated.name
    assert customer["surname"] == mocked_db_customer_updated.surname
    assert customer["photo_url"] == mocked_db_customer_updated.photo_url
    assert customer["creator_id"] == mocked_db_customer_updated.creator_id
    assert customer["modifier_id"] == mocked_db_customer_updated.modifier_id


@pytest.mark.asyncio
async def test_upload_photo_failure(mocker, authenticated_user_client):
    """Test failing to upload a photo by mocking an error response.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mock_upload_file = mocker.MagicMock()
    mock_upload_file.filename = "photo.jpg"
    mock_upload_file.read = b"photo content"

    mocker.patch(
        "app.services.storage_service.S3Client.upload_file",
        side_effect=Exception("Upload failed"),
    )
    mocker.patch(
        "app.db.actions.customer_crud.get_customer",
        return_value=CustomerBase(
            id=1,
            name="Customer 1",
            surname="Customer 1",
            photo_url="http://example.com/photo_new.jpg",
            creator_id=2,
            modifier_id=2,
        ),
    )

    response = await authenticated_user_client.put(
        url=CUSTOMER_UPLOAD_PHOTO_ENDPOINT.format(customer_id=1),
        files={"file": (mock_upload_file.filename, mock_upload_file.read)},
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {
        "detail": "Failed to upload photo to storage: Upload failed",
    }


@pytest.mark.asyncio
async def test_upload_photo_failure_get_customer(
    mocker,
    authenticated_user_client,
):
    """Test uploading a photo for a customer by get_customer.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mock_upload_file = mocker.MagicMock()
    mock_upload_file.filename = "photo.jpg"
    mock_upload_file.read = b"photo content"
    mocker.patch(
        "app.db.actions.customer_crud.get_customer",
        return_value=None,
    )

    response = await authenticated_user_client.put(
        url=CUSTOMER_UPLOAD_PHOTO_ENDPOINT.format(customer_id=1),
        files={"file": (mock_upload_file.filename, mock_upload_file.read)},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Customer not found",
    }


@pytest.mark.asyncio
async def test_upload_photo_failure_updating_customer(
    mocker,
    authenticated_user_client,
):
    """Test uploading a photo for a customer by mocking updating_customer.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mock_photo_url = "http://example.com/photo_new.jpg"
    mock_upload_file = mocker.MagicMock()
    mock_upload_file.filename = "photo.jpg"
    mock_upload_file.read = b"photo content"
    mocker.patch(
        "app.services.storage_service.S3Client.upload_file",
        return_value=mock_photo_url,
    )
    mocked_db_customer = Customer(
        id=1,
        name="Customer 1",
        surname="Customer 1",
        photo_url=None,
        creator_id=12,
        modifier_id=3,
    )
    mocker.patch(
        "app.db.actions.customer_crud.get_customer",
        return_value=mocked_db_customer,
    )
    mocker.patch(
        "app.db.actions.customer_crud.update_customer",
        return_value=None,
    )

    response = await authenticated_user_client.put(
        url=CUSTOMER_UPLOAD_PHOTO_ENDPOINT.format(customer_id=1),
        files={"file": (mock_upload_file.filename, mock_upload_file.read)},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Failed to update customer",
    }


@pytest.mark.asyncio
async def test_upload_photo_failure_without_file(
    mocker,  # noqa
    authenticated_user_client,
):
    """Test uploading a photo for a customer by sending no file.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    response = await authenticated_user_client.put(
        url=CUSTOMER_UPLOAD_PHOTO_ENDPOINT.format(customer_id=1),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "No file provided",
    }


@pytest.mark.asyncio
async def test_upload_photo_failure_wrong_file_format(
    mocker,
    authenticated_user_client,
):
    """Test uploading a photo for a customer by sending the wrong file format.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mock_upload_file = mocker.MagicMock()
    mock_upload_file.filename = "photo.exe"
    mock_upload_file.read = b"photo content"
    mocker.patch(
        "app.db.actions.customer_crud.update_customer",
        return_value=None,
    )

    response = await authenticated_user_client.put(
        url=CUSTOMER_UPLOAD_PHOTO_ENDPOINT.format(customer_id=1),
        files={"file": (mock_upload_file.filename, mock_upload_file.read)},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Invalid file format",
    }


@pytest.mark.asyncio
async def test_upload_photo_failure_empty_file(
    mocker,
    authenticated_user_client,
):
    """Test uploading a photo for a customer by sending empty file.

    Args:
    ----
        mocker (pytest_mock.MockerFixture): Pytest mock fixture.
        authenticated_user_client (AsyncClient): Async HTTP client fixture.

    """
    mock_upload_file = mocker.MagicMock()
    mock_upload_file.filename = "photo.JPg"
    mock_upload_file.read = b""
    mocker.patch(
        "app.db.actions.customer_crud.update_customer",
        return_value=None,
    )

    response = await authenticated_user_client.put(
        url=CUSTOMER_UPLOAD_PHOTO_ENDPOINT.format(customer_id=1),
        files={"file": (mock_upload_file.filename, mock_upload_file.read)},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Uploaded file is empty",
    }
