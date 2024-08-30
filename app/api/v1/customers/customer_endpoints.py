"""Customer management endpoints for the application.

This module defines the routes and handlers for managing customers, including
listing, retrieving, creating, updating, deleting customers, and uploading
photos. It uses FastAPI's APIRouter to set up the endpoints and dependency
injection to ensure that only active admin users can access these routes.

Dependencies:
    - FastAPI
    - SQLAlchemy
    - Pydantic
    - AioBoto3 (for S3 operations)

Endpoints:
    - GET /customers: List all customers.
    - GET /customers/{customer_id}: Retrieve a specific customer by ID.
    - POST /customers: Create a new customer.
    - DELETE /customers/{customer_id}: Delete a specific customer by ID.
    - PUT /customers/{customer_id}: Update a specific customer by ID.
    - PUT /customers/{customer_id}/upload_photo: Upload a photo for a specific customer.
"""

from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import logger, settings
from app.db import db
from app.db.actions import customer_crud, user_crud
from app.db.models.user_model import User
from app.schemas import customer_schemas
from app.schemas.customer_schemas import (
    CustomerBase,
    CustomerCreate,
    CustomerUpdate,
)
from app.services.storage_service import S3Client

CUSTOMER_ENDPOINT = "/customers"
CUSTOMER_DETAIL_ENDPOINT = "/customers/{customer_id}"
CUSTOMER_UPLOAD_PHOTO_ENDPOINT = "/customers/{customer_id}/upload_photo"

logger = logger.get_logger()


class CustomerEndpoints:
    """Customer endpoints."""

    def __init__(self):
        """Initialize the CustomerEndpoints class with routes for managing customers."""
        self.router = APIRouter(tags=["Customer Management"])
        self.router.add_api_route(
            CUSTOMER_ENDPOINT,
            self.list_customers,
            methods=["GET"],
            response_model=List[CustomerBase],
            dependencies=[Depends(user_crud.get_current_active_non_admin_user)],
        )
        self.router.add_api_route(
            CUSTOMER_DETAIL_ENDPOINT,
            self.get_customer,
            methods=["GET"],
            response_model=CustomerBase,
            dependencies=[Depends(user_crud.get_current_active_non_admin_user)],
        )
        self.router.add_api_route(
            CUSTOMER_ENDPOINT,
            self.create_customer,
            methods=["POST"],
            response_model=CustomerBase,
        )
        self.router.add_api_route(
            CUSTOMER_DETAIL_ENDPOINT,
            self.delete_customer,
            methods=["DELETE"],
            dependencies=[Depends(user_crud.get_current_active_non_admin_user)],
        )
        self.router.add_api_route(
            CUSTOMER_DETAIL_ENDPOINT,
            self.update_customer,
            methods=["PUT"],
            response_model=CustomerBase,
        )
        self.router.add_api_route(
            CUSTOMER_UPLOAD_PHOTO_ENDPOINT,
            self.upload_photo,
            methods=["PUT"],
            response_model=CustomerBase,
        )

    def get_router(self):
        """Return the APIRouter instance."""
        return self.router

    async def list_customers(
        self,
        db_session: AsyncSession = Depends(db.get_session),  # noqa
    ) -> List[CustomerBase]:
        """Retrieve a list of all customers."""
        logger.info("Fetching list of customers")
        db_customer_list = await customer_crud.get_all_customers(db_session)
        return [
            customer_schemas.get_customer_schema(db_customer)
            for db_customer in db_customer_list
        ]

    async def get_customer(
        self,
        customer_id: int,
        db_session: AsyncSession = Depends(db.get_session),  # noqa
    ) -> CustomerBase:
        """Retrieve a customer by ID."""
        logger.info(f"Fetching customer with ID: {customer_id}")
        db_customer = await customer_crud.get_customer(
            db_session=db_session,
            customer_id=customer_id,
        )
        if not db_customer:
            logger.error(f"Customer with ID: {customer_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )
        return customer_schemas.get_customer_schema(db_customer)

    async def create_customer(
        self,
        customer_create: CustomerCreate,
        db_session: AsyncSession = Depends(db.get_session),  # noqa
        current_user: User = Depends(  # noqa
            user_crud.get_current_active_non_admin_user,
        ),
    ) -> CustomerBase:
        """Create a new customer."""
        logger.info(f"Creating new customer with data: {customer_create}")
        db_customer = await customer_crud.create_customer(
            db_session=db_session,
            customer=customer_create,
            current_user=current_user,
        )
        return customer_schemas.get_customer_schema(db_customer)

    async def delete_customer(
        self,
        customer_id: int,
        db_session: AsyncSession = Depends(db.get_session),  # noqa
        current_user: User = Depends(  # noqa
            user_crud.get_current_active_non_admin_user,
        ),
    ):
        """Delete a customer by ID."""
        logger.info(f"Deleting customer with ID: {customer_id}")
        customer = await customer_crud.get_customer(
            db_session=db_session,
            customer_id=customer_id,
        )
        if not customer or customer.creator_id != current_user.id:
            logger.error(
                f"Customer with ID: {customer_id} "
                f"not found or not authorized to delete",
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )
        await customer_crud.delete_customer(
            db_session=db_session,
            db_customer=customer,
        )
        logger.info(f"Customer with ID: {customer_id} deleted successfully")
        return {"detail": "Customer deleted"}

    async def update_customer(
        self,
        customer_id: int,
        customer_update: CustomerUpdate,
        db_session: AsyncSession = Depends(db.get_session),  # noqa
        current_user: User = Depends(  # noqa
            user_crud.get_current_active_non_admin_user,
        ),
    ) -> CustomerBase:
        """Update a customer by ID."""
        logger.info(
            f"Updating customer with ID: {customer_id} "
            f"with data: {customer_update}",
        )
        db_customer = await customer_crud.get_customer(
            db_session=db_session,
            customer_id=customer_id,
        )
        if not db_customer:
            logger.error(f"Customer with ID: {customer_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )
        db_customer = await customer_crud.update_customer(
            db_session=db_session,
            db_customer=db_customer,
            customer_update=customer_update,
            current_user_id=current_user.id,
        )

        if db_customer is None:
            logger.error(f"Failed to update customer with ID: {customer_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer update failed",
            )

        return customer_schemas.get_customer_schema(db_customer)

    async def upload_photo(
        self,
        customer_id: int,
        file: UploadFile = File(...),  # noqa
        db_session: AsyncSession = Depends(db.get_session),  # noqa
        current_user: User = Depends(  # noqa
            user_crud.get_current_active_non_admin_user,
        ),
    ) -> CustomerBase:
        """Upload a photo for a customer."""
        if file is None:
            logger.error("No file provided for customer photo upload")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided",
            )

        if not file.filename or "." not in file.filename:
            logger.error("Invalid file format for customer photo upload")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format",
            )

        logger.info(f"Uploading photo for customer ID: {customer_id}")
        db_customer = await customer_crud.get_customer(
            db_session=db_session,
            customer_id=customer_id,
        )
        if not db_customer:
            logger.error(f"Customer with ID: {customer_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )

        file_extension = file.filename.split(".")[-1]
        file_name = f"{uuid4()}.{file_extension}"

        file_bytes = await file.read()

        try:
            s3_client = S3Client()
            photo_url = await s3_client.upload_file(
                bucket_name=settings.load_settings().MINIO_PHOTO_BUCKET_NAME,
                file_bytes=file_bytes,
                file_name=file_name,
            )
            logger.info(
                f"Photo uploaded successfully for customer ID: {customer_id}",
            )
        except Exception as e:
            logger.error(
                f"Failed to upload photo to storage for "
                f"customer ID: {customer_id}. Error: {e}",
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload photo to storage: {e}",
            ) from e

        db_customer = await customer_crud.update_customer(
            db_session=db_session,
            db_customer=db_customer,
            customer_update=CustomerUpdate(photo_url=photo_url),
            current_user_id=current_user.id,
        )

        if db_customer is None:
            logger.error(
                f"Failed to update customer with photo for "
                f"customer ID: {customer_id}",
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to update customer",
            )

        return customer_schemas.get_customer_schema(db_customer)
