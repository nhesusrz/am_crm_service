"""DB models for customers."""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey, orm

from app.db import base

if TYPE_CHECKING:
    from app.db.models.user_model import User


class Customer(base.Base):
    """Customer model."""

    __tablename__ = "customers"  # type: ignore
    id: orm.Mapped[int] = sa.Column(
        sa.Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )  # type: ignore #noqa
    name: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    surname: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    photo_url: orm.Mapped[str | None] = orm.mapped_column(
        sa.String,
        nullable=True,
    )

    creator_id: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        ForeignKey("users.id"),
    )
    modifier_id: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        ForeignKey("users.id"),
    )

    creator: orm.Mapped["User"] = orm.relationship(
        "User",
        back_populates="customers",
        foreign_keys=[creator_id],
    )
    modifier: orm.Mapped["User"] = orm.relationship(
        "User",
        back_populates="modified_customers",
        foreign_keys=[modifier_id],
    )
