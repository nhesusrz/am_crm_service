"""Authentication and authorization utilities.

This module provides functions for managing authentication and authorization,
including creating and verifying JSON Web Tokens (JWT), hashing passwords,
and authenticating users against a database. It uses the `jose` library for
JWT operations and `passlib` for password hashing.

Functions:
    - create_access_token(user_id: int, expires_delta: Union[timedelta, None] =
    None): Creates an access token for a given user ID with an optional
    expiration time.

    - verify_token(token: str):
        Verifies a JWT token and extracts the user ID from it. Raises an H
        TTPException if the token is invalid.

    - hash_password(password: str) -> str:
        Hashes a plain password using bcrypt.

    - verify_password(plain_password: str, hashed_password: str) -> bool:
        Verifies if a plain password matches the hashed password.

    - authenticate_user(db_session: AsyncSession, username: str, password: str,
    is_admin: bool = False):
        Authenticates a user based on username and password, optionally
        checking if the user is an admin.
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
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core import logger, settings
from app.db.models.user_model import User

logger = logger.get_logger()
app_settings = settings.load_settings()

pwd_context = CryptContext(
    schemes=[app_settings.PASS_ALGORITHM],
    deprecated="auto",
)


async def create_access_token(
    user_id: int,
    expires_delta: Union[timedelta, None] = None,
) -> str:
    """Create a JSON Web Token (JWT) for the given user ID.

    Args:
    ----
        user_id (int): The ID of the user for whom the token is created.
        expires_delta (Union[timedelta, None], optional): The duration for
        which the token is valid. If None, defaults to the configured
         token expiration time.

    Returns:
    -------
        str: The encoded JWT as a string.

    """
    logger.info(f"Creating access token for user ID: {user_id}")
    to_encode = {"id": user_id}
    if expires_delta:
        expire = datetime.now(pytz.utc) + expires_delta
    else:
        expire = datetime.now(pytz.utc) + timedelta(
            minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    to_encode["exp"] = int(expire.timestamp())

    token = jwt.encode(
        to_encode,
        app_settings.TOKEN_SECRET_KEY,
        algorithm=app_settings.TOKEN_ALGORITHM,
    )
    logger.info(f"Access token created with expiration time: {expire}")
    return token


async def verify_token(token: str) -> int | None:
    """Verify a JSON Web Token (JWT) and extract the user ID.

    Args:
    ----
        token (str): The JWT to be verified.

    Returns:
    -------
        int | None: The user ID extracted from the token if valid,
        or `None` if the token is invalid or the user ID is not found
        in the token.

    """
    logger.info("Verifying token...")
    try:
        payload = jwt.decode(
            token,
            app_settings.TOKEN_SECRET_KEY,
            algorithms=[app_settings.TOKEN_ALGORITHM],
        )
        user_id = payload.get("id")
        if user_id is None:
            logger.error("Token payload does not contain user ID")
            return None
        logger.info(f"Token verified for user ID: {user_id}")
        return user_id
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        return None


def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt.

    Args:
    ----
        password (str): The plain password to be hashed.

    Returns:
    -------
        str: The hashed password.

    """
    logger.info("Hashing password")
    hashed_password = pwd_context.hash(password)
    logger.info("Password hashed successfully")
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
    ----
        plain_password (str): The plain password to be verified.
        hashed_password (str): The hashed password to compare against.

    Returns:
    -------
        bool: True if the plain password matches the hashed password,
        False otherwise.

    """
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
    """Authenticate a user by username and password.

    Args:
    ----
        db_session (AsyncSession): The database session to use for querying
        the user.
        username (str): The username of the user to authenticate.
        password (str): The password to verify.
        is_admin (bool, optional): Whether to check for admin privileges.
        Defaults to False.

    Returns:
    -------
        Union[User, None]: The authenticated user object if credentials
        are valid, otherwise None.

    Raises:
    ------
        SQLAlchemyError: If there is an error querying the database.

    """
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
