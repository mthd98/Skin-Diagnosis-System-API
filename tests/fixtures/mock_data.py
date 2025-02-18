"""Mock data for testing the Skin Diagnosis System API."""

from datetime import datetime
from datetime import timezone
import uuid

from app.schema.case import CaseCreate
from app.schema.case import DiagnosisResult
from app.schema.doctor import DoctorCreate
from app.schema.patient import PatientCreate

# Mock doctor data
MOCK_DOCTOR = DoctorCreate(
    name="Dr. Jane Smith",
    email="janesmith@example.com",
    password="securepassword",
).dict()
MOCK_DOCTOR["doctor_id"] = str(uuid.uuid4())
MOCK_DOCTOR["created_at"] = datetime.now(timezone.utc)

# Mock patient data
MOCK_PATIENT = PatientCreate(
    patient_number=54321,
    name="John Doe",
    date_of_birth=datetime(1985, 8, 25, tzinfo=timezone.utc),
    gender="Male",
    country="UK",
    occupation="Engineer",
    ethnicity="Hispanic",
    notes=["Allergic to penicillin"],
).dict()
MOCK_PATIENT["patient_id"] = str(uuid.uuid4())
MOCK_PATIENT["created_at"] = datetime.now(timezone.utc)

# Mock case data
MOCK_CASE = CaseCreate(
    doctor_id=uuid.UUID(MOCK_DOCTOR["doctor_id"]),
    patient_id=uuid.UUID(MOCK_PATIENT["patient_id"]),
    diagnosis=DiagnosisResult(malignant=0.1, benign=0.9),
    notes="Follow-up required",
).dict()
MOCK_CASE["case_id"] = str(uuid.uuid4())
MOCK_CASE["created_at"] = datetime.now(timezone.utc)

# List of mock data
MOCK_DATA = {"doctor": MOCK_DOCTOR, "patient": MOCK_PATIENT, "case": MOCK_CASE}
