"""Login endpoints for user and admin authentication and token management.

This module provides endpoints for user login, admin login, and token refresh
functionalities.
It uses FastAPI for creating and managing API routes and SQLAlchemy for
asynchronous database operations.
The endpoints facilitate authentication and token management, including
generating and refreshing access tokens.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.login.login_models import (
    RefreshTokenRequest,
    TokenResponseModel,
)
from app.core import logger, settings
from app.core.security import (
    authenticate_user,
    create_access_token,
    verify_token,
)
from app.db import db
from app.db.models.user_model import User

USER_LOGIN_ENDPOINT = "/login"
REFRESH_TOKEN_ENDPOINT = "/token/refresh"
ADMIN_LOGIN_ENDPOINT = "/admin/login"

logger = logger.get_logger()
app_settings = settings.load_settings()


class LoginEndpoints:
    """Define API endpoints for user, admin, authentication and token mgmt."""

    def __init__(self):
        """Initialize the LoginEndpoints class and sets up API routes."""
        self.router = APIRouter(tags=["Auth Login"])
        self.router.add_api_route(
            ADMIN_LOGIN_ENDPOINT,
            self.admin_login_for_access_token,
            methods=["POST"],
            response_model=TokenResponseModel,
        )
        self.router.add_api_route(
            USER_LOGIN_ENDPOINT,
            self.user_login_for_access_token,
            methods=["POST"],
            response_model=TokenResponseModel,
        )
        self.router.add_api_route(
            REFRESH_TOKEN_ENDPOINT,
            self.refresh_access_token,
            methods=["POST"],
            response_model=TokenResponseModel,
        )

    def get_router(self):
        """Return the FastAPI router instance."""
        return self.router

    async def admin_login_for_access_token(
        self,
        form_data: OAuth2PasswordRequestForm = Depends(),  # noqa
        db_session: AsyncSession = Depends(db.get_session),  # noqa
    ) -> TokenResponseModel:
        """Handle login req for admin users and returns an access token."""
        db_user = await authenticate_user(
            db_session=db_session,
            username=form_data.username,
            password=form_data.password,
            is_admin=True,
        )

        if db_user is None:
            logger.warning(
                f"Admin login failed for username: {form_data.username}",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        logger.info(
            f"Admin login successful for username: {form_data.username}",
        )
        return await self._generate_token_response_model(db_user=db_user)

    async def user_login_for_access_token(
        self,
        form_data: OAuth2PasswordRequestForm = Depends(),  # noqa
        db_session: AsyncSession = Depends(db.get_session),  # noqa
    ):
        """Handle login req for regular users and returns an access token."""
        db_user = await authenticate_user(
            db_session=db_session,
            username=form_data.username,
            password=form_data.password,
            is_admin=False,
        )

        if db_user is None:
            logger.warning(
                f"User login failed for username: {form_data.username}",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        logger.info(
            f"User login successful for username: {form_data.username}",
        )
        return await self._generate_token_response_model(db_user=db_user)

    async def refresh_access_token(
        self,
        request: RefreshTokenRequest,
    ) -> TokenResponseModel:
        """Handle requests to refresh an access token."""
        try:
            username = await verify_token(request.refresh_token)
            if not username:
                logger.warning("Invalid refresh token used")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token_expires = timedelta(
                minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            )
            new_access_token = await create_access_token(
                user_id=username,
                expires_delta=access_token_expires,
            )
            logger.info(f"Access token refreshed for username: {username}")
            return TokenResponseModel(
                access_token=new_access_token,
                token_type="bearer",
            )
        except Exception as e:
            logger.error(f"Error refreshing access token: {str(e)}")
            raise HTTPException(  # noqa
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def _generate_token_response_model(self, db_user: User) -> TokenResponseModel:
        """Generates an access token response model for the given user.

        Args:
        ----
            db_user (User): The db user for whom the token is created.

        Returns:
        -------
        TokenResponseModel: The access token and its type ("bearer").

        """
        access_token_expires = timedelta(
            minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        access_token = await create_access_token(
            user_id=db_user.id,
            expires_delta=access_token_expires,
        )
        logger.info(f"Access token created for user ID: {db_user.id}")
        return TokenResponseModel(
            access_token=access_token,
            token_type="bearer",
        )
