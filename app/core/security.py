"""Authentication and authorization utilities.

This module provides functions for managing authentication and authorization,
including creating and verifying JSON Web Tokens (JWT), hashing passwords,
and authenticating users against a database. It uses the `jose` library for
JWT operations and `passlib` for password hashing.

Functions:
    - create_access_token(user_id: int, expires_delta: Union[timedelta, None] = None):
        Creates an access token for a given user ID with an optional expiration time.

    - verify_token(token: str):
        Verifies a JWT token and extracts the user ID from it. Raises an HTTPException
        if the token is invalid.

    - hash_password(password: str) -> str:
        Hashes a plain password using bcrypt.

    - verify_password(plain_password: str, hashed_password: str) -> bool:
        Verifies if a plain password matches the hashed password.

    - authenticate_user(db_session: AsyncSession, username: str, password: str,
    is_admin: bool = False):
        Authenticates a user based on username and password, optionally checking
        if the user is an admin.
        Returns the user object if authentication is successful, otherwise
        returns False.

Dependencies:
    - datetime: Provides date and time manipulation.
    - typing: Provides type hints for function signatures.
    - fastapi: Web framework used for handling HTTP requests and exceptions.
    - jose: Library used for JWT encoding and decoding.
    - passlib: Library used for hashing and verifying passwords.
    - sqlalchemy: ORM used for interacting with the database.
"""

from datetime import datetime, timedelta
from typing import Union

import pytz
from fastapi import HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status

from app.core import logger, settings
from app.db.models.user_model import User

logger = logger.get_logger()

pwd_context = CryptContext(
    schemes=[settings.load_settings().PASS_ALGORITHM],
    deprecated="auto",
)


async def create_access_token(
    user_id: int,
    expires_delta: Union[timedelta, None] = None,
) -> str:
    """Create a JSON Web Token (JWT) for the given user ID."""
    logger.info(f"Creating access token for user ID: {user_id}")
    to_encode = {"id": user_id}
    if expires_delta:
        expire = datetime.now(pytz.utc) + expires_delta
    else:
        expire = datetime.now(pytz.utc) + timedelta(
            minutes=settings.load_settings().ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    to_encode["exp"] = int(expire.timestamp())

    token = jwt.encode(
        to_encode,
        settings.load_settings().TOKEN_SECRET_KEY,
        algorithm=settings.load_settings().TOKEN_ALGORITHM,
    )
    logger.info(f"Access token created with expiration time: {expire}")
    return token


async def verify_token(token: str) -> int:
    """Verify a JSON Web Token (JWT) and extract the user ID."""
    logger.info("Verifying token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.load_settings().TOKEN_SECRET_KEY,
            algorithms=[settings.load_settings().TOKEN_ALGORITHM],
        )
        user_id = payload.get("id")
        if user_id is None:
            logger.error("Token payload does not contain user ID")
            raise credentials_exception
        logger.info(f"Token verified for user ID: {user_id}")
        return user_id
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        raise credentials_exception  # noqa


def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt."""
    logger.info("Hashing password")
    hashed_password = pwd_context.hash(password)
    logger.info("Password hashed successfully")
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    logger.info("Verifying password")
    is_valid = pwd_context.verify(plain_password, hashed_password)
    if is_valid:
        logger.info("Password verified successfully")
    else:
        logger.warning("Password verification failed")
    return is_valid


async def authenticate_user(
    db_session: AsyncSession,
    username: str,
    password: str,
    is_admin: bool = False,  # noqa
) -> User | None:
    """Authenticate a user by username and password."""
    logger.info(f"Authenticating user: {username}, is_admin={is_admin}")
    query = select(User).filter(
        User.username == username,
        User.is_admin == is_admin,
    )
    try:
        result = await db_session.execute(query)
    except SQLAlchemyError as exc:
        logger.error(f"Database error during authentication: {exc}")
        raise exc
    db_user = result.unique().scalars().first()
    if not db_user or not verify_password(password, db_user.hashed_password):
        logger.warning(f"Authentication failed for user: {username}")
        return None
    logger.info(f"User {username} authenticated successfully")
    return db_user
