"""Main app file."""

import logging

from fastapi import FastAPI

from app.api.v1.routers import register_routers
from app.core import settings


def create_app() -> FastAPI:
    """Return a FastAPI app object."""
    web_app = FastAPI(
        title=settings.load_settings().PROJECT_NAME,
        openapi_url=f"{settings.load_settings().API_V1_STR}/openapi.json",
        version="0.1.0",
    )

    register_routers(app=web_app)

    logger = logging.getLogger("uvicorn")
    logger.info("AM CRM Service is running")

    return web_app


app = create_app()
