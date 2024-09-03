"""Customer Schemas Module.

This module defines Pydantic schemas for customer-related data and provides
a function to convert a database Customer model instance to a schema
instance. The schemas are used for validating and serializing customer data
for API requests and responses.

Classes:
- CustomerBase: Base schema for customer data, including ID, name, surname,
photo URL, and creator/modifier IDs.
- CustomerCreate: Schema for creating a new customer, extending CustomerBase
without additional fields.
- CustomerUpdate: Schema for updating customer information, with optional
fields for name, surname, photo URL, and modifier ID.

Functions:
- get_customer_schema: Converts a database Customer model instance into a
CustomerBase schema instance.
"""

from typing import Optional

from pydantic import BaseModel

from app.db.models.customer_model import Customer


class CustomerBase(BaseModel):
    """Schema for customer data.

    Attributes
    ----------
        id (int): The unique identifier of the customer.
        name (str): The name of the customer.
        surname (str): The surname of the customer.
        photo_url (Optional[str]): The URL of the customer's photo
        (default: None).
        creator_id (int): The ID of the user who created the customer
        record.
        modifier_id (int): The ID of the user who last modified the
        customer record.

    Config:
        from_attributes (bool): Allows creation of the schema from ORM models'
        attributes.

    """

    id: int
    name: str
    surname: str
    photo_url: Optional[str] = None
    creator_id: int
    modifier_id: int

    class Config:
        """Configuration for the CustomerBase schema."""

        from_attributes = True


class CustomerCreate(BaseModel):
    """Schema for creating a new customer.

    Attributes
    ----------
        name (str): The name of the customer (inherited from CustomerBase).
        surname (str): The surname of the customer (inherited from
        CustomerBase).
        photo_url (Optional[str]): The URL of the customer's photo
        (inherited from CustomerBase).

    """

    name: str
    surname: str
    photo_url: Optional[str] = None


class CustomerUpdate(BaseModel):
    """Schema for updating customer information.

    Attributes
    ----------
        name (Optional[str]): The new name of the customer, if being updated.
        surname (Optional[str]): The new surname of the customer, if being
        updated.
        photo_url (Optional[str]): The new photo URL of the customer, if being
        updated.
        modifier_id (Optional[int]): The ID of the user who is modifying
        the customer record, if being updated.

    """

    name: Optional[str] = None
    surname: Optional[str] = None
    photo_url: Optional[str] = None
    modifier_id: Optional[int] = None


def get_customer_schema(
    db_customer_model: Customer,
) -> CustomerBase:
    """Convert a database Customer model to a CustomerBase schema instance.

    Args:
    ----
        db_customer_model (Customer): The Customer database model instance.

    Returns:
    -------
        CustomerBase: The CustomerBase schema instance containing the
        customer's data.

    """
    return CustomerBase(
        id=db_customer_model.id,
        name=db_customer_model.name,
        surname=db_customer_model.surname,
        photo_url=db_customer_model.photo_url,
        creator_id=db_customer_model.creator_id,
        modifier_id=db_customer_model.modifier_id,
    )
