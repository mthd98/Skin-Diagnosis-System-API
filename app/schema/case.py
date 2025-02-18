"""Pydantic schemas for case validation with image support."""

from datetime import datetime
from datetime import timezone
from typing import List, Optional
import uuid

from pydantic import BaseModel
from pydantic import Field


class DiagnosisResult(BaseModel):
    """Schema representing the diagnosis result with probabilities for each condition.

    Attributes:
        malignant (Optional[float]): Probability of the condition being malignant.
        benign (Optional[float]): Probability of the condition being benign.
    """

    malignant: Optional[float] = Field(
        None, description="Probability of malignancy."
    )
    benign: Optional[float] = Field(
        None, description="Probability of benign condition."
    )


class CaseBase(BaseModel):
    """Base schema for a case.

    Attributes:
        doctor_id (uuid.UUID): Unique identifier for the doctor handling the case.
        patient_id (uuid.UUID): Unique identifier for the patient.
        diagnosis (Optional[DiagnosisResult]): The diagnosis result with probabilities.
        notes (Optional[str]): Notes related to the case.
        created_at (datetime): Timestamp of case creation (UTC).
    """

    doctor_id: uuid.UUID
    patient_id: uuid.UUID
    diagnosis: Optional[DiagnosisResult] = None
    notes: Optional[List[str]] = Field(
        default_factory=list, description="Notes related to the case."
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of case creation (UTC).",
    )


class CaseCreate(CaseBase):
    """Schema for creating a new case.

    Inherits from:
        CaseBase: Base schema with required attributes.
    """

    pass


class Case(CaseBase):
    """Schema for a case stored in the database.

    Attributes:
        case_id (uuid.UUID): Unique identifier for the case.
        image_id (str): URL to access the uploaded image.
    """

    case_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for the case.",
    )
    image_id: Optional[str] = Field(
        None, description="URL to access the uploaded image."
    )
