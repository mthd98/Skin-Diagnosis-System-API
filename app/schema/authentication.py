from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    """Schema for login request (only doctors can log in)."""
    email: EmailStr = Field(..., description="Email address for login")
    password: str = Field(..., description="Password for login")

class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Type of token issued")
