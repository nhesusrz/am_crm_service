"""Customer CRUD tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.db.actions.customer_crud import (
    create_customer,
    delete_customer,
    get_all_customers,
    get_customer,
    update_customer,
)
from app.db.models.customer_model import Customer
from app.db.models.user_model import User
from app.schemas.customer_schemas import CustomerCreate, CustomerUpdate

CUSTOMER_ID = 1
USER_ID = 1
NAME = "Carl"
SURNAME = "Max"
PHOTO_URL = "http://example.com/photo.jpg"
UPDATED_NAME = "Antonio"
UPDATED_SURNAME = "Escotado"
UPDATED_PHOTO_URL = "http://example.com/new_photo.jpg"


@pytest.mark.asyncio
async def test_get_all_customers():
    """Test retrieving all customers from the database."""
    mock_db_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.unique.return_value.scalars.return_value.all.return_value = [
        Customer(
            id=CUSTOMER_ID,
            name=NAME,
            surname=SURNAME,
            photo_url=PHOTO_URL,
            creator_id=USER_ID,
            modifier_id=USER_ID,
        ),
    ]
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    customers = await get_all_customers(mock_db_session)

    assert len(customers) == 1
    assert customers[0].name == NAME
    assert customers[0].surname == SURNAME


@pytest.mark.asyncio
async def test_get_customer():
    """Test retrieving a specific customer by ID."""
    mock_db_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Customer(
        id=CUSTOMER_ID,
        name=NAME,
        surname=SURNAME,
        photo_url=PHOTO_URL,
        creator_id=USER_ID,
        modifier_id=USER_ID,
    )
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    customer = await get_customer(mock_db_session, CUSTOMER_ID)

    assert customer is not None
    assert customer.id == CUSTOMER_ID
    assert customer.name == NAME
    assert customer.surname == SURNAME


@pytest.mark.asyncio
async def test_create_customer():
    """Test creating a new customer."""
    mock_db_session = AsyncMock()
    mock_db_session.add = MagicMock()
    mock_db_session.commit = AsyncMock()

    current_user = User(id=USER_ID)
    customer_create = CustomerCreate(
        name=NAME,
        surname=SURNAME,
        photo_url=PHOTO_URL,
    )

    mock_db_session.execute = AsyncMock()
    mock_db_session.commit = AsyncMock()

    mock_db_session.add = MagicMock()
    mock_db_session.commit = AsyncMock()

    async def mock_commit():
        pass

    mock_db_session.commit = mock_commit

    created_customer = await create_customer(
        mock_db_session,
        customer_create,
        current_user,
    )

    assert created_customer is not None
    assert created_customer.name == NAME
    assert created_customer.surname == SURNAME
    assert created_customer.photo_url == PHOTO_URL


@pytest.mark.asyncio
async def test_delete_customer():
    """Test deleting a customer."""
    mock_db_session = AsyncMock()
    mock_db_session.delete = AsyncMock()
    mock_db_session.commit = AsyncMock()

    customer = Customer(
        id=CUSTOMER_ID,
        name=NAME,
        surname=SURNAME,
        photo_url=PHOTO_URL,
        creator_id=USER_ID,
        modifier_id=USER_ID,
    )

    await delete_customer(mock_db_session, customer)

    mock_db_session.delete.assert_called_once_with(customer)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_customer():
    """Test updating an existing customer record."""
    mock_db_session = AsyncMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock()

    existing_customer = Customer(
        id=CUSTOMER_ID,
        name=NAME,
        surname=SURNAME,
        photo_url=PHOTO_URL,
        creator_id=USER_ID,
        modifier_id=USER_ID,
    )

    customer_update = CustomerUpdate(
        name=UPDATED_NAME,
        surname=UPDATED_SURNAME,
        photo_url=UPDATED_PHOTO_URL,
    )

    mock_db_session.execute = AsyncMock(return_value=MagicMock())
    mock_db_session.commit = AsyncMock()

    updated = await update_customer(
        mock_db_session,
        existing_customer,
        customer_update,
        USER_ID,
    )

    assert updated is not None
    assert updated.name == UPDATED_NAME
    assert updated.surname == UPDATED_SURNAME
    assert updated.photo_url == UPDATED_PHOTO_URL
