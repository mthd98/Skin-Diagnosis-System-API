"""Pydantic schemas for patient management."""

from datetime import date
from datetime import datetime
from datetime import timezone
from typing import List, Optional
import uuid

from pydantic import BaseModel
from pydantic import Field


class PatientCreate(BaseModel):
    """Schema for creating a new patient.

    Attributes:
        patient_number (int): Patient number provided during registration (must be positive).
        name (str): Full name of the patient.
        date_of_birth (datetime): Date of birth of the patient.
        gender (str): Gender of the patient.
        country (Optional[str]): Country of the patient.
        occupation (Optional[str]): Occupation of the patient.
        ethnicity (Optional[str]): Ethnicity of the patient.
        notes (Optional[List[str]]): Notes related to the patient (defaults to an empty list).
    """

    patient_number: int = Field(
        ...,
        gt=0,
        description="Patient number provided during registration (must be positive).",
    )
    name: str = Field(..., description="Full name of the patient.")
    date_of_birth: date = Field(
        ..., description="Date of birth of the patient in YYYY-MM-DD format."
    )
    gender: str = Field(..., description="Gender of the patient.")
    country: Optional[str] = Field(None, description="Country of the patient.")
    occupation: Optional[str] = Field(
        None, description="Occupation of the patient."
    )
    ethnicity: Optional[str] = Field(
        None, description="Ethnicity of the patient."
    )
    notes: Optional[List[str]] = Field(
        default_factory=list, description="Notes related to the patient."
    )


class Patient(PatientCreate):
    """Schema representing a patient in the system.

    Attributes:
        patient_id (uuid.UUID): Unique identifier for the patient.
        created_at (datetime): Timestamp of patient record creation (UTC).
    """

    patient_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for the patient.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of patient record creation (UTC).",
    )
