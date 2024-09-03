"""User Schemas Module.

This module defines Pydantic schemas for user-related data and provides
a function to convert a database User model instance to a schema
instance. The schemas are used for validating and serializing user
data for API requests and responses.

Classes:
- UserBase: Base schema for user data, including ID, username, and admin
status.
- UserCreateRequest: Schema for creating a new user, extending UserBase
and adding a password field.
- UserUpdate: Schema for updating user information, with optional fields
for username, admin status, and password.

Functions:
- get_user_schema: Converts a database User model instance into a UserBase
schema instance.
"""

from typing import Optional

from pydantic import BaseModel

from app.db.models.user_model import User


class UserBase(BaseModel):
    """Schema for user data.

    Attributes
    ----------
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        is_admin (bool): Indicates if the user has admin privileges
         (default: False).

    Config:
        from_attributes (bool): Allows creation of the schema from
        ORM models'
        attributes.

    """

    id: int
    username: str
    is_admin: bool = False

    class Config:
        """Configuration for the UserBase schema."""

        from_attributes = True


class UserCreate(BaseModel):
    """Schema for creating a new user.

    Attributes
    ----------
        username (str): The username of the user.
        password (str): The password for the new user.
        is_admin (bool): Indicates if the user should have admin privileges
        (default: False).

    """

    username: str
    password: str
    is_admin: bool = False


class UserUpdate(BaseModel):
    """Schema for updating user information.

    Attributes
    ----------
        username (Optional[str]): The new username of the user,
        if being updated.
        is_admin (Optional[bool]): The new admin status of the user,
        if being updated.
        password (Optional[str]): The new password of the user, if being
        updated.

    """

    username: Optional[str] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = None


def get_user_schema(
    db_user_model: User,
) -> UserBase:
    """Convert a database User model instance to a UserBase schema instance.

    Args:
    ----
        db_user_model (User): The User database model instance.

    Returns:
    -------
        UserBase: The UserBase schema instance containing the user's data.

    """
    return UserBase(
        id=db_user_model.id,
        username=db_user_model.username,
        is_admin=db_user_model.is_admin,
    )
