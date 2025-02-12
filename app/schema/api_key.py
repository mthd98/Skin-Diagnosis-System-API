import uuid
from pydantic import BaseModel, Field
from datetime import datetime

class UserAPIKey(BaseModel):
    """Schema representing API keys associated with doctors."""
    api_key_id: uuid.UUID = Field(..., description="Unique identifier for the API key")
    doctor_id: uuid.UUID = Field(..., description="Unique identifier of the doctor linked to the API key")
    api_key: str = Field(..., description="The actual API key")
    expired_date: datetime = Field(..., description="Expiration date of the API key")
    usage: int = Field(..., description="Usage count for the API key")

class APIKey(BaseModel):
    """Schema representing an API key associated with a doctor."""
    api_key: str = Field(..., description="The actual API key")
    expired_date: datetime = Field(..., description="Expiration date of the API key")