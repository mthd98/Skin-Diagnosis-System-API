import uuid
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

class Patient(BaseModel):
    """Schema representing a patient in the system (created by doctors)."""
    patient_id: uuid.UUID = Field(..., description="Unique identifier for the patient")
    patient_number: int = Field(..., description="Unique patient number")
    doctor_id: uuid.UUID = Field(..., description="Unique identifier of the doctor who created the patient profile")
    name: str = Field(..., description="Name of the patient")
    date_of_birth: datetime = Field(..., description="Date of birth of the patient")
    gender: str = Field(..., description="Gender of the patient")
    country: Optional[str] = Field(None, description="Country of the patient")
    occupation: Optional[str] = Field(None, description="Occupation of the patient")
    ethnicity: Optional[str] = Field(None, description="Ethnicity of the patient")
    notes: Optional[List[str]] = Field(default_factory=list, description="Notes related to the patient")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of patient record creation")

class PatientCreate(BaseModel):
    """Schema for creating a new patient. Includes patient_number."""
    patient_number: int = Field(..., description="Patient number provided during registration")
    name: str = Field(..., description="Name of the patient")
    date_of_birth: datetime = Field(..., description="Date of birth of the patient")
    gender: str = Field(..., description="Gender of the patient")
    country: Optional[str] = Field(None, description="Country of the patient")
    occupation: Optional[str] = Field(None, description="Occupation of the patient")
    ethnicity: Optional[str] = Field(None, description="Ethnicity of the patient")
    notes: Optional[List[str]] = Field(default_factory=list, description="Notes related to the patient")
