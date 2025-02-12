"""Pydantic schemas for case validation with image support."""

from typing import List, Optional
import uuid
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class DiagnosisResult(BaseModel):
    """
    Schema representing the diagnosis result with probabilities for each condition.
    """
    malignant: Optional[float] = Field(None, description="Probability of the condition being malignant.")
    benign: Optional[float] = Field(None, description="Probability of the condition being benign.")

class CaseBase(BaseModel):
    """Base schema for a case."""
    doctor_id: uuid.UUID
    patient_id: uuid.UUID
    diagnosis: Optional[DiagnosisResult] = Field(None, description="The diagnosis result with probabilities.")
    notes: Optional[str] = Field(default_factory=list, description="Notes related to the case")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of case creation.")


class CaseCreate(CaseBase):
    """Schema for creating a new case."""
    pass


class Case(CaseBase):
    """Schema for a case stored in the database."""
    case_id: uuid.UUID = Field(..., description="Unique identifier for the case.")
    image_id: str = Field(None, description="URL to access the uploaded image.")
