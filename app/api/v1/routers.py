"""Application router setup for the FastAPI application.

This module sets up the routing for the FastAPI application, including
the inclusion of various API routers for handling authentication,
user management, and customer management endpoints. It also includes
a route for serving the `robots.txt` file to control web crawlers' access.

Classes:
    - Routers: Manages the instantiation of routers for different endpoints.

Functions:
    - register_routers(app: FastAPI): Registers all API routers with the FastAPI
    application.
    - Includes routes for login, users, and customers.
    - Adds a static route for `robots.txt` to control access by web crawlers.
"""

from fastapi import FastAPI
from starlette.responses import PlainTextResponse

from app.api.v1.auth.login import login_endpoints
from app.api.v1.customers import customer_endpoints
from app.api.v1.users import user_endpoints
from app.core import settings


class Routers:
    """Holds and initializes API endpoint routers for the application.

    Attributes
    ----------
        login_endpoints (LoginEndpoints): Router for login-related endpoints.
        user_endpoints (UserEndpoints): Router for user management endpoints.
        customer_endpoints (CustomerEndpoints): Router for customer management
        endpoints.

    """

    login_endpoints = login_endpoints.LoginEndpoints()
    customer_endpoints = customer_endpoints.CustomerEndpoints()
    user_endpoints = user_endpoints.UserEndpoints()


def register_routers(app: FastAPI):
    """Register API routers with the FastAPI application.

    Args:
    ----
        app (FastAPI): The FastAPI application instance to register the routers with.

    This function includes the routers for login, user management, and customer
    management. It also sets up a route for serving `robots.txt` to control web
    crawler access.

    """
    api_routers = Routers()

    @app.get("/robots.txt", response_class=PlainTextResponse)
    def robots():
        """Serve the `robots.txt` file for web crawlers.

        Returns
        -------
            PlainTextResponse: A plain text response with instructions for web crawlers.

        """
        return """User-agent: *\nDisallow: /"""

    # Routers setup
    app.include_router(
        api_routers.login_endpoints.get_router(),
        prefix=settings.load_settings().API_V1_STR,
    )
    app.include_router(
        api_routers.user_endpoints.get_router(),
        prefix=settings.load_settings().API_V1_STR,
    )
    app.include_router(
        api_routers.customer_endpoints.get_router(),
        prefix=settings.load_settings().API_V1_STR,
    )
