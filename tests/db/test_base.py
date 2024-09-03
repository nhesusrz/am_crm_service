"""DB base model tests."""

from datetime import datetime

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

from app.db.base import Base


class TestModel(Base):
    """Test model tests."""

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


def test_tablename():
    """Test that the __tablename__ attribute is correctly generated.

    This test verifies that the table name for TestModel is the lowercase
    version class name.

    Asserts
    -------
        str: The table name generated matches the expected lowercase class
        name.
    """
    assert TestModel.__tablename__ == "testmodel"  # type: ignore


def test_timestamps(engine, setup_database):  # noqa
    """Test that the created_at and updated_at columns initialized.

    Args:
    ----
        engine (Engine): The SQLAlchemy engine used for database operations.
        setup_database (None): Fixture that sets up and tears down the database
        schema.


    Asserts
    -------
        datetime: The created_at and updated_at timestamps are not None.

    """
    session = sessionmaker(bind=engine)()
    new_record = TestModel(name="Test Name")
    session.add(new_record)
    session.commit()

    assert new_record.created_at is not None
    assert new_record.updated_at is not None
    assert isinstance(new_record.created_at, datetime)
    assert isinstance(new_record.updated_at, datetime)


def test_update_timestamps(engine, setup_database):  # noqa
    """Test that the updated_at column is correctly updated.

    Args:
    ----
        engine (Engine): The SQLAlchemy engine used for database operations.
        setup_database (None): Fixture that sets up and tears down the database
        schema.


    Asserts
    -------
        datetime: The updated_at timestamp is updated to a new value after
        modifying the record.

    """
    session = sessionmaker(bind=engine)()
    new_record = TestModel(name="Initial Name")
    session.add(new_record)
    session.commit()

    original_updated_at = new_record.updated_at

    new_record.name = "Updated Name"  # type: ignore
    session.commit()

    assert new_record.updated_at > original_updated_at
