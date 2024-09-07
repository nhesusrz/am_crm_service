"""User CRUD Operations Module.

This module contains functions for performing CRUD (Create, Read, Update,
Delete) operations on user data. It also includes a function to retrieve the
currently active admin user based on an OAuth2 token.

Functions:
- get_all_users: Retrieve all users from the database.
- get_user: Retrieve a specific user by their ID.
- create_user: Create a new user in the database.
- delete_user: Delete a user from the database.
- update_user: Update an existing user's information.
- get_current_active_admin: Verify an OAuth2 token and return the active admin
user.

Dependencies:
- FastAPI: For handling HTTP requests and OAuth2 token parsing.
- SQLAlchemy: For database interactions.
- Passlib: For password hashing and verification.
- Starlette: For HTTP status codes.
"""

from typing import List

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status

from app.core import logger
from app.core.security import hash_password, verify_token
from app.db import db
from app.db.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate

logger = logger.get_logger()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_all_users(db_session: AsyncSession) -> List[User]:
    """Retrieve all users from the database."""
    logger.info("Retrieving all users from the database")
    query = select(User)
    result = await db_session.execute(query)
    users = list(result.unique().scalars().all())
    logger.info(f"Found {len(users)} users")
    return users


async def get_user(db_session: AsyncSession, user_id: int) -> User | None:
    """Retrieve a specific user by their ID."""
    logger.info(f"Retrieving user with ID: {user_id}")
    query = select(User).filter(User.id == user_id)
    result = await db_session.execute(query)
    user = result.scalar_one_or_none()
    if user:
        logger.info(f"User with ID: {user_id} found")
    else:
        logger.warning(f"User with ID: {user_id} not found")
    return user


async def create_user(db_session: AsyncSession, user: UserCreate) -> User:
    """Create a new user in the database."""
    logger.info(f"Creating a new user with username: {user.username}")
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        is_admin=user.is_admin,
    )
    await db_session.add(db_user)
    try:
        await db_session.commit()
        logger.info(f"User created with ID: {db_user.id}")
    except SQLAlchemyError as exc:
        await db_session.rollback()
        logger.error(f"Error creating user: {exc}")
        raise exc
    return db_user


async def delete_user(db_session: AsyncSession, user: User) -> None:
    """Delete a user from the database."""
    logger.info(f"Deleting user with ID: {user.id}")
    await db_session.delete(user)
    try:
        await db_session.commit()
        logger.info(f"User with ID: {user.id} deleted")
    except SQLAlchemyError as exc:
        await db_session.rollback()
        logger.error(f"Error deleting user: {exc}")
        raise exc


async def update_user(
    db_session: AsyncSession,
    db_user: User,
    user_request: UserUpdate,
) -> User:
    """Update an existing user's information."""
    logger.info(f"Updating user with ID: {db_user.id}")
    if user_request.username:
        db_user.username = user_request.username
    if user_request.password:
        db_user.hashed_password = hash_password(user_request.password)
    if user_request.is_admin is not None:
        db_user.is_admin = user_request.is_admin
    try:
        await db_session.commit()
        logger.info(f"User with ID: {db_user.id} updated")
    except SQLAlchemyError as exc:
        await db_session.rollback()
        logger.error(f"Error updating user: {exc}")
        raise exc
    await db_session.refresh(db_user)
    return db_user


async def get_current_active_user(
    token: str = Depends(oauth2_scheme),  # type: ignore
    db_session: AsyncSession = Depends(db.get_session),  # type: ignore # noqa
    is_admin: bool = True,  # noqa
) -> User:
    """Verify the OAuth2 token and return the active admin user."""
    logger.info("Verifying OAuth2 token")
    user_id = await verify_token(token)
    if user_id is None:
        logger.warning("Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    query = select(User).filter_by(id=user_id)

    result = await db_session.execute(query)

    if result is None:
        logger.warning(f"User with ID: {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db_user = result.unique().scalars().first()

    if is_admin and not db_user.is_admin:
        logger.warning(
            f"User with ID: {user_id} does not have admin permissions",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    logger.info(f"Active user with ID: {user_id} retrieved")
    return db_user


async def get_current_active_non_admin_user(
    token: str = Depends(oauth2_scheme),  # type: ignore
    db_session: AsyncSession = Depends(db.get_session),  # type: ignore # noqa
) -> User:
    """Wrap to get the current active user without admin check."""
    logger.info("Retrieving current active non-admin user")
    return await get_current_active_user(
        token=token,
        is_admin=False,
        db_session=db_session,
    )
