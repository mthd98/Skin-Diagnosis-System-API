"""Pydantic schemas for doctor management."""

from datetime import datetime
from datetime import timezone
import uuid

from app.schema.api_key import APIKey
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class DoctorBase(BaseModel):
    """Base schema for a doctor.

    Attributes:
        email (EmailStr): Email address of the doctor.
        name (str): Full name of the doctor.
    """

    email: EmailStr = Field(..., description="Email address of the doctor.")
    name: str = Field(..., description="Full name of the doctor.")


class DoctorCreate(DoctorBase):
    """Schema for creating a new doctor account.

    Attributes:
        password (str): Password for the doctor's account.
    """

    password: str = Field(..., description="Password for the doctor's account.")


class DoctorDB(DoctorBase):
    """Schema for a doctor stored in the database.

    Attributes:
        doctor_id (uuid.UUID): Unique identifier for the doctor.
        created_at (datetime): Timestamp of doctor account creation (UTC).
    """

    doctor_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for the doctor.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of doctor account creation (UTC).",
    )


class DoctorProfile(DoctorDB):
    """Schema representing the full doctor profile, including API key details.

    Attributes:
        api_key (APIKey): API key details associated with the doctor.
    """

    api_key: APIKey = Field(
        ..., description="API key details associated with the doctor."
    )
