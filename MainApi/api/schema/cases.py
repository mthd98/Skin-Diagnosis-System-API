"""Pydantic schemas for case validation with image support."""

import uuid
from pydantic import BaseModel

class CaseBase(BaseModel):
    """Base schema for a case."""
    doctor_id: uuid.uuid4
    patient_id: uuid.uuid4
    diagnosis: str
    notes: str

class CaseCreate(CaseBase):
    """Schema for creating a new case."""

class CaseDB(CaseBase):
    """Schema for a case stored in the database."""
    id: uuid.uuid4
    image_url: str = None  # URL to access uploaded image
