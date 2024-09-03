"""Login models module."""

from pydantic import BaseModel


class TokenResponseModel(BaseModel):
    """Model for representing the response containing an access token.

    This model is used to encapsulate the details of an authentication
    response, which includes the access token and its type.

    Attributes
    ----------
        access_token (str): The JWT access token that can be used to access
        protected resources.
        token_type (str): The type of token issued, typically "bearer".

    """

    access_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    """Model for representing the request to refresh an access token.

    This model is used to encapsulate the details required to request a new
    access token using a refresh token.

    Attributes
    ----------
        refresh_token (str): The refresh token used to get a new access
        token.

    """

    refresh_token: str
