"""Pydantic schemas for authentication and login requests."""

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class LoginRequest(BaseModel):
    """Schema for login request (only doctors can log in).

    Attributes:
        email (EmailStr): Email address for login (validated format).
        password (str): Password for login.
    """

    email: EmailStr = Field(..., description="Email address for login.")
    password: str = Field(..., description="Password for login.")


class TokenResponse(BaseModel):
    """Schema for JWT token response.

    Attributes:
        access_token (str): JWT access token issued after authentication.
        token_type (str): Type of token issued, defaults to 'bearer'.
    """

    access_token: str = Field(..., description="JWT access token.")
    token_type: str = Field(
        default="bearer",
        description="Type of token issued (default: 'bearer').",
    )
