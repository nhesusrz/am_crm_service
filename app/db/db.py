"""Main Database Module.

This module provides functionality for managing the asynchronous database
engine and sessions using SQLAlchemy. It includes functions to create and
configure the database engine and session maker, and context managers for
handling asynchronous database sessions.

Functions:
- get_engine: Retrieve the asynchronous database engine.
- get_async_session_maker: Retrieve the asynchronous session maker.
- get_session_context_manager: Retrieve an asynchronous context manager
for managing database sessions.
- get_session: Retrieve an asynchronous database session for use in FastAPI
dependency injection.

Dependencies:
- SQLAlchemy: For managing asynchronous database interactions.
- Functools: For caching the database engine instance.
- Typing: For type annotations.
"""

from contextlib import asynccontextmanager
from functools import lru_cache
from typing import AsyncContextManager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core import settings


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Retrieve the asynchronous database engine.

    This function creates and returns an instance of the SQLAlchemy
    AsyncEngine, which is used to connect to the database asynchronously.
    The engine is configured using settings loaded from the application's
    configuration.

    Returns
    -------
        AsyncEngine: The SQLAlchemy AsyncEngine instance.

    Notes
    -----
        The engine instance is cached to avoid creating multiple instances
        and improve performance.

    """
    app_settings = settings.load_settings()
    db_uri = app_settings.SQLALCHEMY_DATABASE_URI
    if db_uri is None:
        raise ValueError(
            "SQLALCHEMY_DATABASE_URI is not set in the configuration.",
        )
    return create_async_engine(
        db_uri,  # Database URL from settings
        echo=False,
        future=True,
        pool_size=app_settings.SQLALCHEMY_POOL_SIZE,
        max_overflow=app_settings.SQLALCHEMY_MAX_OVERFLOW,
    )


def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    """Retrieve the asynchronous session maker.

    This function creates and returns an instance of async_sessionmaker,
    which is used to create asynchronous database sessions. The session
    maker is bound to the SQLAlchemy AsyncEngine.

    Returns
    -------
        async_sessionmaker[AsyncSession]: The SQLAlchemy async_sessionmaker
        instance.

    """
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


@asynccontextmanager  # type: ignore
async def get_session_context_manager() -> (
    AsyncContextManager[AsyncSession]
):  # type: ignore
    """Retrieve an asynchronous context manager for managing database sessions.

    This context manager is used to create and manage asynchronous database
    sessions. It ensures that sessions are properly closed after use.

    Yields
    ------
        AsyncSession: The asynchronous database session.

    Notes
    -----
        This function provides a context manager for managing sessions
        and is typically used with the `async with` statement.

    """
    async_session_maker = get_async_session_maker()
    async with async_session_maker() as session:
        yield session  # type: ignore


async def get_session() -> AsyncSession:  # type: ignore
    """Retrieve an asynchronous database session.

    This function provides a dependency for FastAPI that returns an
    asynchronous database session.
    It ensures that the session is properly managed and closed after use.

    Returns
    -------
        AsyncSession: The asynchronous database session.

    Notes
    -----
        This function is intended to be used as a dependency in FastAPI
        routes to provide database access.

    """
    async with get_session_context_manager() as session:
        yield session  # type: ignore
