"""DB tests."""

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db import db


@pytest.mark.asyncio
async def test_get_engine():
    """Test that the get_engine function returns a valid AsyncEngine instance."""
    engine = db.get_engine()
    assert engine is not None
    assert isinstance(engine, type(create_async_engine("sqlite+aiosqlite://")))


@pytest.mark.asyncio
async def test_get_async_session_maker():
    """Test the function returns a valid async_sessionmaker instance."""
    async_session_maker = db.get_async_session_maker()
    assert async_session_maker is not None
    assert isinstance(async_session_maker, async_sessionmaker)


@pytest.mark.asyncio
async def test_get_session_context_manager():
    """Test the function provides a valid async session."""
    async with db.get_session_context_manager() as session:
        assert session is not None
        assert isinstance(session, AsyncSession)


@pytest.mark.asyncio
async def test_get_session():
    """Test that the get_session function provides a valid async session ."""
    async for session in db.get_session():  # type: ignore
        assert session is not None
        assert isinstance(session, AsyncSession)
