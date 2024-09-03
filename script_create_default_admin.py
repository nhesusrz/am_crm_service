"""Creates the default admin user for the app."""

import asyncio

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core import settings
from app.db import db
from app.db.actions.user_crud import create_user
from app.db.models.user_model import User
from app.schemas.user_schemas import UserCreate


async def create_default_admin(db_session: AsyncSession):
    """Create a default admin user if it does not already exist.

    Args:
    ----
        db_session (AsyncSession): The SQLAlchemy asynchronous session used to
        interact with the database.

    Returns:
    -------
        None: The function does not return a value but prints messages to
        indicate the outcome.

    """
    query = select(func.count()).select_from(User).filter(User.is_admin)
    result = await db_session.execute(query)
    user_count = result.scalar()
    if user_count and user_count > 0:
        print("Admin user already exists on the service app.")
        return

    default_admin_user = UserCreate(
        username=settings.load_settings().DEFAULT_ADMIN_USER,
        password=settings.load_settings().DEFAULT_ADMIN_PASSWORD,
        is_admin=True,
    )

    db_user = await create_user(db_session=db_session, user=default_admin_user)
    if db_user:
        print(
            f"The default admin user created successfully! "
            f"User/Password: {settings.load_settings().DEFAULT_ADMIN_USER}/"
            f"{settings.load_settings().DEFAULT_ADMIN_PASSWORD}",
        )
    else:
        print("The default admin could not be created!")


async def main():
    """Call entry point for the script to create the default admin user."""
    async with db.get_session_context_manager() as session:
        await create_default_admin(session)


if __name__ == "__main__":
    asyncio.run(main())
