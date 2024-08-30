"""Alembic configuration file."""

# We need to include asyncio for Async support
import asyncio

from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import the APP Config
from app.core import settings

# MAKE SURE TO IMPORT ALL MODELS HERE
# DO NOT CHANGE OR REMOVE THIS IMPORTS! Needed for auto-generation of Alembic migrations
from app.db import base  # noqa
from app.db import models  # noqa # pylint: disable=unused-import

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config  # noqa # pylint: disable=no-member

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = base.Base.metadata  # noqa # pylint: disable=no-member


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(  # pylint: disable=no-member
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():  # pylint: disable=no-member
        context.run_migrations()  # pylint: disable=no-member


def do_run_migrations(connection: Connection):
    """Run migrations in 'async' mode."""
    context.configure(  # pylint: disable=no-member
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():  # pylint: disable=no-member
        context.run_migrations()  # pylint: disable=no-member


async def run_async_migrations():
    """Run migrations in 'async' mode.

    In this scenario we need to create an AsyncEngine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.load_settings().SQLALCHEMY_DATABASE_URI  # type: ignore
    connectable = async_engine_from_config(
        configuration,  # type: ignore
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():  # pylint: disable=no-member
    run_migrations_offline()
else:
    run_migrations_online()
