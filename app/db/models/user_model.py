"""DB models for the users."""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import orm

from app.db import base

if TYPE_CHECKING:
    from app.db.models.customer_model import Customer


class User(base.Base):
    """User model."""

    __tablename__ = "users"  # type: ignore
    id: orm.Mapped[int] = sa.Column(sa.Integer, primary_key=True, autoincrement=True)  # type: ignore
    username: orm.Mapped[str] = orm.mapped_column(
        sa.String,
        nullable=False,
        unique=True,
    )
    hashed_password: orm.Mapped[str] = orm.mapped_column(
        sa.String,
        nullable=False,
    )
    is_admin: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=False)

    customers: orm.Mapped[list["Customer"]] = orm.relationship(
        "Customer",
        back_populates="creator",
        foreign_keys="[Customer.creator_id]",
    )
    modified_customers: orm.Mapped[list["Customer"]] = orm.relationship(
        "Customer",
        back_populates="modifier",
        foreign_keys="[Customer.modifier_id]",
    )
