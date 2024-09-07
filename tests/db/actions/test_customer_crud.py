"""Customer CRUD tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

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

    customers = await get_all_customers(db_session=mock_db_session)

    assert len(customers) == 1
    assert customers[0].name == NAME
    assert customers[0].surname == SURNAME


@pytest.mark.asyncio
async def test_get_all_customers_empty():
    """Test retrieving all customers from the database."""
    mock_db_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.unique.return_value.scalars.return_value.all.return_value = []
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    customers = await get_all_customers(db_session=mock_db_session)

    assert len(customers) == 0


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

    customer = await get_customer(
        db_session=mock_db_session,
        customer_id=CUSTOMER_ID,
    )

    assert customer is not None
    assert customer.id == CUSTOMER_ID
    assert customer.name == NAME
    assert customer.surname == SURNAME


@pytest.mark.asyncio
async def test_get_non_existing_customer():
    """Test retrieving a specific customer by wrong ID."""
    mock_db_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    customer = await get_customer(
        db_session=mock_db_session,
        customer_id=CUSTOMER_ID,
    )

    assert not customer


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
        db_session=mock_db_session,
        customer=customer_create,
        current_user=current_user,
    )

    assert created_customer is not None
    assert created_customer.name == NAME
    assert created_customer.surname == SURNAME
    assert created_customer.photo_url == PHOTO_URL

    @pytest.mark.asyncio
    async def test_create_customer_failure():
        """Test creating a new customer."""
        mock_db_session = AsyncMock()
        mock_db_session.add = AsyncMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.commit.side_effect = SQLAlchemyError("Database error")

        current_user = User(id=USER_ID)
        customer_create = CustomerCreate(
            name=NAME,
            surname=SURNAME,
            photo_url=PHOTO_URL,
        )

        with pytest.raises(SQLAlchemyError):
            await create_customer(
                db_session=mock_db_session,
                customer=customer_create,
                current_user=current_user,
            )

            mock_db_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_customer_success():
    """Test deleting a customer successfully."""
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

    await delete_customer(db_session=mock_db_session, db_customer=customer)

    mock_db_session.delete.assert_called_once_with(customer)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_customer_failure():
    """Test deleting a customer without success."""
    mock_db_session = AsyncMock()
    mock_db_session.delete = AsyncMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.commit.side_effect = SQLAlchemyError("Database error")

    customer = Customer(
        id=CUSTOMER_ID,
        name=NAME,
        surname=SURNAME,
        photo_url=PHOTO_URL,
        creator_id=USER_ID,
        modifier_id=USER_ID,
    )

    with pytest.raises(SQLAlchemyError):
        await delete_customer(db_session=mock_db_session, db_customer=customer)

        mock_db_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_customer_success():
    """Test updating an existing customer record with success."""
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
        db_session=mock_db_session,
        db_customer=existing_customer,
        customer_update=customer_update,
        current_user_id=USER_ID,
    )

    assert updated is not None
    assert updated.name == UPDATED_NAME
    assert updated.surname == UPDATED_SURNAME
    assert updated.photo_url == UPDATED_PHOTO_URL


@pytest.mark.asyncio
async def test_update_customer_failure():
    """Test updating an existing customer record without success."""
    mock_db_session = AsyncMock()
    mock_db_session.refresh = AsyncMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.commit.side_effect = SQLAlchemyError("Database error")

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

    with pytest.raises(SQLAlchemyError):
        await update_customer(
            mock_db_session,
            existing_customer,
            customer_update,
            USER_ID,
        )

        mock_db_session.rollback.assert_awaited_once()
