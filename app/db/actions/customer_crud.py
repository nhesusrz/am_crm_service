"""Customer CRUD Operations Module.

This module provides asynchronous functions for performing CRUD operations
on customer records in the database. It includes functions for retrieving all
customers, retrieving a specific customer by ID, creating a new customer,
deleting an existing customer, and updating customer information.

Functions:
- get_all_customers: Retrieve all customer records from the database.
- get_customer: Retrieve a specific customer record by its ID.
- create_customer: Create a new customer record in the database.
- delete_customer: Delete an existing customer record from the database.
- update_customer: Update an existing customer record in the database.

Dependencies:
- SQLAlchemy: For managing asynchronous database interactions.
- Typing: For type annotations.
"""

from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core import logger
from app.db.models.customer_model import Customer
from app.db.models.user_model import User
from app.schemas.customer_schemas import CustomerCreate, CustomerUpdate

logger = logger.get_logger()


async def get_all_customers(db_session: AsyncSession) -> List[Customer]:
    """Retrieve all customer records from the database."""
    logger.info("Retrieving all customer records")
    query = select(Customer)
    result = await db_session.execute(query)
    customers = list(result.unique().scalars().all())
    logger.info(f"Found {len(customers)} customers")
    return customers


async def get_customer(
    db_session: AsyncSession,
    customer_id: int,
) -> Customer | None:
    """Retrieve a specific customer record by its ID."""
    logger.info(f"Retrieving customer with ID: {customer_id}")
    query = select(Customer).filter(Customer.id == customer_id)
    result = await db_session.execute(query)
    customer = result.scalar_one_or_none()
    if customer:
        logger.info(f"Customer with ID: {customer_id} found")
    else:
        logger.warning(f"Customer with ID: {customer_id} not found")
    return customer


async def create_customer(
    db_session: AsyncSession,
    customer: CustomerCreate,
    current_user: User,
) -> Customer:
    """Create a new customer record in the database."""
    logger.info(f"Creating a new customer with name: {customer.name}")
    db_customer = Customer(
        name=customer.name,
        surname=customer.surname,
        photo_url=str(customer.photo_url) if customer.photo_url else None,
        creator_id=current_user.id,
        modifier_id=current_user.id,
    )
    db_session.add(db_customer)
    try:
        await db_session.commit()
        logger.info(f"Customer created with ID: {db_customer.id}")
    except SQLAlchemyError as exc:
        await db_session.rollback()
        logger.error(f"Error creating customer: {exc}")
        raise exc
    return db_customer


async def delete_customer(
    db_session: AsyncSession,
    db_customer: Customer,
) -> None:
    """Delete an existing customer record from the database."""
    logger.info(f"Deleting customer with ID: {db_customer.id}")
    await db_session.delete(db_customer)
    try:
        await db_session.commit()
        logger.info(f"Customer with ID: {db_customer.id} deleted")
    except SQLAlchemyError as exc:
        await db_session.rollback()
        logger.error(f"Error deleting customer: {exc}")
        raise exc


async def update_customer(
    db_session: AsyncSession,
    db_customer: Customer,
    customer_update: CustomerUpdate,
    current_user_id: int,
) -> Customer | None:
    """Update an existing customer record in the database."""
    logger.info(f"Updating customer with ID: {db_customer.id}")
    if customer_update.name:
        db_customer.name = customer_update.name
    if customer_update.surname:
        db_customer.surname = customer_update.surname
    if customer_update.photo_url:
        db_customer.photo_url = (
            str(customer_update.photo_url)
            if customer_update.photo_url
            else None
        )
    db_customer.modifier_id = current_user_id
    try:
        await db_session.commit()
        logger.info(f"Customer with ID: {db_customer.id} updated")
    except SQLAlchemyError as exc:
        await db_session.rollback()
        logger.error(f"Error updating customer: {exc}")
        raise exc
    await db_session.refresh(db_customer)
    return db_customer
