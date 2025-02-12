import uuid
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
from app.schema.api_key import APIKey

class DoctorBase(BaseModel):
    """Base schema for a doctor."""
    email: EmailStr = Field(..., description="Email address of the doctor")
    name: str = Field(..., description="Name of the doctor")

class DoctorCreate(DoctorBase):
    """Schema for creating a new doctor account."""
    password: str = Field(..., description="Password for the doctor's account")

class DoctorDB(DoctorBase):
    """Schema for a doctor stored in the database."""
    doctor_id: uuid.UUID = Field(..., description="Unique identifier for the doctor")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of doctor account creation")
    
class DoctorProfile(DoctorDB):
    """Schema representing the full doctor profile, including API key details."""
    api_key: APIKey = Field(..., description="API key details associated with the doctor")
    
class APIKey(BaseModel):
    """Schema representing an API key associated with a doctor."""
    api_key: str = Field(..., description="The actual API key")
    expired_date: datetime = Field(..., description="Expiration date of the API key") 