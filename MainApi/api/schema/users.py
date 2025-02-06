"""Pydantic schemas for user validation."""

import uuid
from pydantic import BaseModel, EmailStr, Field, constr

# User Role Constants
DOCTOR = "doctor"
PATIENT = "patient"
SUPERUSER = "superuser"
VALID_ROLES = {DOCTOR, PATIENT, SUPERUSER}

class UserBase(BaseModel):
    """Base schema for a user."""
    email: EmailStr
    full_name: str
    role: constr(pattern=f"^({'|'.join(VALID_ROLES)})$")

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str

class UserDB(UserBase):
    """Schema for a user stored in the database."""
    id: uuid.UUID

# -------- Authentication Schemas --------

class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
