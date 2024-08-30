"""Main file tests."""

import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core import settings
from app.main import create_app


@pytest.fixture
def app() -> FastAPI:
    """Fixture that provides the FastAPI app instance."""
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Fixture that provides a TestClient instance for the FastAPI app."""
    return TestClient(app)


def test_create_app_instance(app: FastAPI):
    """Test that create_app returns an instance of FastAPI."""
    assert isinstance(app, FastAPI)


def test_app_title(app: FastAPI):
    """Test that the FastAPI app title is correctly set."""
    assert app.title == settings.load_settings().PROJECT_NAME


def test_openapi_url(app: FastAPI):
    """Test that the OpenAPI URL is correctly set."""
    assert app.openapi_url == "/api/v1/openapi.json"


def test_logger_info(caplog):
    """Test that the logger outputs the correct information."""
    with caplog.at_level(logging.INFO):
        create_app()

    assert "AM CRM Service is running" in caplog.text
