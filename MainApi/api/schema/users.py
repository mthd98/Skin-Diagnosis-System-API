"""Pydantic schemas for user validation."""

import uuid
from pydantic import BaseModel, EmailStr, Field

# User Role Constants
DOCTOR = "doctor"
PATIENT = "patient"
SUPERUSER = "superuser"
VALID_ROLES = {DOCTOR, PATIENT, SUPERUSER}

class UserBase(BaseModel):
    """Base schema for a user."""
    email: EmailStr
    full_name: str
    role: str = Field(..., regex=f"^({'|'.join(VALID_ROLES)})$")

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str

class UserDB(UserBase):
    """Schema for a user stored in the database."""
    id: uuid.uuid4
