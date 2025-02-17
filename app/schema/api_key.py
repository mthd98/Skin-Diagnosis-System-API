"""Pydantic schemas for API key management."""

from datetime import datetime
import uuid

from pydantic import BaseModel
from pydantic import Field


class UserAPIKey(BaseModel):
    """Schema representing API keys associated with doctors.

    Attributes:
        api_key_id (uuid.UUID): Unique identifier for the API key.
        doctor_id (uuid.UUID): Unique identifier of the doctor linked to the API key.
        api_key (str): The actual API key.
        expired_date (datetime): Expiration date of the API key (UTC).
        usage (int): Usage count for the API key.
    """

    api_key_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for the API key.",
    )
    doctor_id: uuid.UUID = Field(
        ...,
        description="Unique identifier of the doctor linked to the API key.",
    )
    api_key: str = Field(..., description="The actual API key.")
    expired_date: datetime = Field(
        ..., description="Expiration date of the API key (UTC)."
    )
    usage: int = Field(default=1000, description="Usage count for the API key.")


class APIKey(BaseModel):
    """Schema representing an API key associated with a doctor.

    Attributes:
        api_key (str): The actual API key.
        expired_date (datetime): Expiration date of the API key (UTC).
    """

    api_key: str = Field(..., description="The actual API key.")
    expired_date: datetime = Field(
        ..., description="Expiration date of the API key (UTC)."
    )
