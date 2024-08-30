"""DB customer model tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.customer_model import Customer
from app.db.models.user_model import User

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.mark.asyncio
async def test_create_customer(
    async_db_session: AsyncSession,
    create_user: User,
):
    """Test the creation of a Customer.

    Args:
    ----
        async_db_session (AsyncSession): The SQLAlchemy async session for database
        interactions.
        create_user (User): The User fixture that provides a user for the Customer
        creation.

    """
    new_customer = Customer(
        name="John",
        surname="Doe",
        photo_url=None,
        creator_id=create_user.id,
        modifier_id=create_user.id,
    )
    async_db_session.add(new_customer)
    await async_db_session.commit()
    await async_db_session.refresh(new_customer)

    assert new_customer.id is not None
    assert new_customer.name == "John"
    assert new_customer.surname == "Doe"
    assert new_customer.creator_id == create_user.id
    assert new_customer.modifier_id == create_user.id

    query = select(Customer).filter_by(id=new_customer.id)
    result = await async_db_session.execute(query)
    customer_from_db = result.scalar_one()

    assert customer_from_db.id == new_customer.id
    assert customer_from_db.name == "John"
    assert customer_from_db.surname == "Doe"
    assert customer_from_db.creator_id == create_user.id
    assert customer_from_db.modifier_id == create_user.id
