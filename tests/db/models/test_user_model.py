"""DB user model tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.util.preloaded import orm

from app.db.models.customer_model import Customer
from app.db.models.user_model import User


@pytest.mark.asyncio
async def test_create_user(async_db_session: AsyncSession):
    """Test creating a new user.

    Args:
    ----
        async_db_session (AsyncSession): The SQLAlchemy async session object
        for database operations.

    """
    user = User(username="testuser", hashed_password="hashedpassword123")
    async_db_session.add(user)
    await async_db_session.commit()

    query = select(User).filter_by(username="testuser")
    result = await async_db_session.execute(query)
    db_user = result.scalar_one_or_none()

    assert db_user is not None
    assert db_user.username == "testuser"
    assert db_user.hashed_password == "hashedpassword123"
    assert db_user.is_admin is False


@pytest.mark.asyncio
async def test_update_user(async_db_session: AsyncSession):
    """Test updating a user.

    Args:
    ----
        async_db_session (AsyncSession): The SQLAlchemy async session object.

    """
    user = User(username="testuser", hashed_password="hashedpassword123")
    async_db_session.add(user)
    await async_db_session.commit()

    user.username = "updateduser"
    user.is_admin = True
    await async_db_session.commit()

    query = select(User).filter_by(id=user.id)
    result = await async_db_session.execute(query)
    db_user = result.scalar_one_or_none()

    assert db_user is not None
    assert db_user.username == "updateduser"
    assert db_user.is_admin is True


@pytest.mark.asyncio
async def test_delete_user(async_db_session: AsyncSession):
    """Test deleting a user.

    Args:
    ----
        async_db_session (AsyncSession): The SQLAlchemy async session object.

    """
    user = User(username="testuser", hashed_password="hashedpassword123")
    async_db_session.add(user)
    await async_db_session.commit()

    await async_db_session.delete(user)
    await async_db_session.commit()

    query = select(User).filter_by(username="testuser")
    result = await async_db_session.execute(query)
    db_user = result.scalar_one_or_none()

    assert db_user is None


@pytest.mark.asyncio
async def test_user_relationships(async_db_session: AsyncSession):
    """Test user relationships with customers.

    Args:
    ----
        async_db_session (AsyncSession): The SQLAlchemy async session object.

    """
    user = User(username="testuser", hashed_password="hashedpassword123")
    async_db_session.add(user)
    await async_db_session.commit()

    customer1 = Customer(
        name="John",
        surname="Doe",
        creator_id=user.id,
        modifier_id=user.id,
    )
    customer2 = Customer(
        name="Jane",
        surname="Doe",
        creator_id=user.id,
        modifier_id=user.id,
    )
    customer_count = 2
    async_db_session.add_all([customer1, customer2])
    await async_db_session.commit()

    query = (
        select(User)
        .filter_by(id=user.id)
        .options(orm.joinedload(User.customers))
    )
    result = await async_db_session.execute(query)
    db_user = result.unique().scalar_one_or_none()

    assert db_user is not None
    assert len(db_user.customers) == customer_count
    assert db_user.customers[0].name == "John"
    assert db_user.customers[1].name == "Jane"
