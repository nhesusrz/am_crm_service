"""Base Class for SQLAlchemy Models.

This module defines a base class for SQLAlchemy ORM models that provides common
fields and automatic table name generation. The `Base` class inherits from both
`AsyncAttrs` and `orm.DeclarativeBase` to support asynchronous database
operations and declarative model definitions.

Attributes
----------
- id: A unique identifier for the model (type hint: Any).
- created_at: A timestamp indicating when the record was created. Automatically
set to the current UTC time on creation.
- updated_at: A timestamp indicating the last time the record was updated.
Automatically updated to the current UTC time on modification.

Methods
-------
- __tablename__: A class-level method that generates the table name for the
model by converting the class name to lowercase.

Inherits:
- AsyncAttrs: Provides support for asynchronous attributes.
- orm.DeclarativeBase: The base class for SQLAlchemy ORM declarative models,
which allows for defining models using the declarative API.

Usage:
This class should be inherited by all SQLAlchemy ORM models to include common
fields and to leverage automatic table name generation based on the model's
class name.

"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, orm
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, orm.DeclarativeBase):
    """Base Class for SQLAlchemy Models.

    This base class is intended to be inherited by all SQLAlchemy ORM models
    to provide common fields and functionality. It includes automatic
    handling of `created_at` and `updated_at` timestamps and generates
    the table name based on the class name.

    Attributes
    ----------
        id (Any): A unique identifier for the model.
        created_at (orm.Mapped[datetime]): Timestamp for when the record was
        created. Defaults to current UTC time.
        updated_at (orm.Mapped[datetime]): Timestamp for when the record was
        last updated. Automatically updated to current UTC time.

    Methods
    -------
        __tablename__ (str): Generates the table name based on the model class
        name in lowercase.

    Inherits:
        AsyncAttrs: Allows for asynchronous attribute handling.
        orm.DeclarativeBase: Provides the base functionality for SQLAlchemy ORM
        declarative models.

    """

    id: Any

    created_at: orm.Mapped[datetime] = orm.mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: orm.Mapped[datetime] = orm.mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __name__: str

    @orm.declared_attr  # type: ignore
    def __tablename__(self) -> str:
        """Generate the table name automatically based on the class name.

        Returns
        -------
            str: The table name, which is the lowercase version of the class
            name.

        """
        return self.__name__.lower()
