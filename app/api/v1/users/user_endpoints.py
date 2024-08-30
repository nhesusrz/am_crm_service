"""User management endpoints for the application.

This module defines the routes and handlers for managing users, including
listing, retrieving, creating, updating, and deleting users. It uses
FastAPI's APIRouter to set up the endpoints and dependency injection to
ensure that only active admin users can access these routes.

Dependencies:
    - FastAPI
    - SQLAlchemy
    - Pydantic

Endpoints:
    - GET /users: List all users.
    - GET /users/{user_id}: Retrieve a specific user by ID.
    - POST /users: Create a new user.
    - DELETE /users/{user_id}: Delete a specific user by ID.
    - PUT /users/{user_id}: Update a specific user by ID.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core import logger
from app.db import db
from app.db.actions import user_crud
from app.schemas import user_schemas
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate

USER_ENDPOINT = "/users"
USER_DETAIL_ENDPOINT = "/users/{user_id}"

logger = logger.get_logger()


class UserEndpoints:
    """User endpoints."""

    def __init__(self):
        """Initialize the UserEndpoints class with routes for managing users."""
        self.router = APIRouter(tags=["User Management"])
        self.router.add_api_route(
            USER_ENDPOINT,
            self.list_users,
            methods=["GET"],
            response_model=List[UserBase],
            dependencies=[Depends(user_crud.get_current_active_user)],
        )
        self.router.add_api_route(
            USER_DETAIL_ENDPOINT,
            self.get_user,
            methods=["GET"],
            response_model=UserBase,
            dependencies=[Depends(user_crud.get_current_active_user)],
        )
        self.router.add_api_route(
            USER_ENDPOINT,
            self.create_user,
            methods=["POST"],
            response_model=UserBase,
            dependencies=[Depends(user_crud.get_current_active_user)],
        )
        self.router.add_api_route(
            USER_DETAIL_ENDPOINT,
            self.delete_user,
            methods=["DELETE"],
            dependencies=[Depends(user_crud.get_current_active_user)],
        )
        self.router.add_api_route(
            USER_DETAIL_ENDPOINT,
            self.update_user,
            methods=["PUT"],
            response_model=UserBase,
            dependencies=[Depends(user_crud.get_current_active_user)],
        )

    def get_router(self):
        """Return the APIRouter instance."""
        return self.router

    async def list_users(
        self,
        db_session: AsyncSession = Depends(db.get_session),  # noqa
    ) -> List[UserBase]:
        """Retrieve a list of all users."""
        logger.info("Fetching list of users")
        db_user_list = await user_crud.get_all_users(db_session=db_session)
        return [
            user_schemas.get_user_schema(db_user) for db_user in db_user_list
        ]

    async def get_user(
        self,
        user_id: int,
        db_session: AsyncSession = Depends(db.get_session),  # noqa
    ) -> UserBase:
        """Retrieve a user by ID."""
        logger.info(f"Fetching user with ID: {user_id}")
        db_user = await user_crud.get_user(
            db_session=db_session,
            user_id=user_id,
        )
        if not db_user:
            logger.error(f"User with ID: {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user_schemas.get_user_schema(db_user)

    async def create_user(
        self,
        user_create: UserCreate,
        db_session: AsyncSession = Depends(db.get_session),  # noqa
    ) -> UserBase:
        """Create a new user."""
        logger.info(f"Creating new user with data: {user_create}")
        db_user = await user_crud.create_user(
            db_session=db_session,
            user=user_create,
        )
        return user_schemas.get_user_schema(db_user)

    async def delete_user(
        self,
        user_id: int,
        db_session: AsyncSession = Depends(db.get_session),  # noqa
    ):
        """Delete a user by ID."""
        logger.info(f"Deleting user with ID: {user_id}")
        user = await user_crud.get_user(db_session=db_session, user_id=user_id)
        if not user:
            logger.error(f"User with ID: {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        await user_crud.delete_user(db_session=db_session, user=user)
        logger.info(f"User with ID: {user_id} deleted successfully")
        return {"detail": "User deleted"}

    async def update_user(
        self,
        user_id: int,
        user_update: UserUpdate,
        db_session: AsyncSession = Depends(db.get_session),  # noqa
    ) -> UserBase:
        """Update a user by ID."""
        logger.info(
            f"Updating user with ID: {user_id} with data: {user_update}",
        )
        db_user = await user_crud.get_user(
            db_session=db_session,
            user_id=user_id,
        )
        if not db_user:
            logger.error(f"User with ID: {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        db_user = await user_crud.update_user(
            db_session=db_session,
            db_user=db_user,
            user_request=user_update,
        )
        return user_schemas.get_user_schema(db_user)
