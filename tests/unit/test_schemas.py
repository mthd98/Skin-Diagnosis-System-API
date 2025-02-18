from datetime import datetime
from datetime import timezone
import uuid

from app.schema.api_key import APIKey
from app.schema.case import Case
from app.schema.case import DiagnosisResult
from app.schema.doctor import DoctorCreate
from app.schema.doctor import DoctorDB
from app.schema.patient import Patient
from app.schema.patient import PatientCreate
import pytest


@pytest.mark.order(1)
def test_api_key_schema():
    """Test APIKey schema instantiation."""
    api_key = APIKey(
        api_key="test_api_key", expired_date=datetime.now(timezone.utc)
    )
    assert api_key.api_key == "test_api_key"
    assert isinstance(api_key.expired_date, datetime)


@pytest.mark.order(2)
def test_diagnosis_result_schema():
    """Test DiagnosisResult schema instantiation."""
    diagnosis = DiagnosisResult(malignant=0.8, benign=0.2)
    assert diagnosis.malignant == 0.8
    assert diagnosis.benign == 0.2


@pytest.mark.order(3)
def test_case_schema():
    """Test Case schema instantiation."""
    case = Case(
        doctor_id=uuid.uuid4(),
        patient_id=uuid.uuid4(),
        diagnosis=DiagnosisResult(malignant=0.9, benign=0.1),
        notes=["Suspicious mole detected"],
        created_at=datetime.now(timezone.utc),
        case_id=uuid.uuid4(),
        image_id="test_image_id",
    )
    assert isinstance(case.doctor_id, uuid.UUID)
    assert isinstance(case.patient_id, uuid.UUID)
    assert isinstance(case.diagnosis, DiagnosisResult)
    assert case.notes == ["Suspicious mole detected"]


@pytest.mark.order(4)
def test_doctor_schema():
    """Test DoctorCreate and DoctorDB schema instantiation."""
    doctor_create = DoctorCreate(
        name="Dr. Jane Doe", email="jane.doe@example.com", password="securepass"
    )
    assert doctor_create.name == "Dr. Jane Doe"
    assert doctor_create.email == "jane.doe@example.com"

    doctor_db = DoctorDB(
        doctor_id=uuid.uuid4(),
        name="Dr. Jane Doe",
        email="jane.doe@example.com",
        created_at=datetime.now(timezone.utc),
    )
    assert isinstance(doctor_db.doctor_id, uuid.UUID)
    assert isinstance(doctor_db.created_at, datetime)


@pytest.mark.order(5)
def test_patient_schema():
    """Test PatientCreate and Patient schema instantiation."""
    patient_create = PatientCreate(
        patient_number=12345,
        name="John Doe",
        date_of_birth=datetime(1985, 8, 25, tzinfo=timezone.utc),
        gender="Male",
        country="UK",
        occupation="Engineer",
        ethnicity="Hispanic",
        notes=["Allergic to penicillin"],
    )
    assert patient_create.name == "John Doe"
    assert patient_create.gender == "Male"

    patient = Patient(
        patient_id=uuid.uuid4(),
        patient_number=12345,
        name="John Doe",
        date_of_birth=datetime(1985, 8, 25, tzinfo=timezone.utc),
        gender="Male",
        country="UK",
        occupation="Engineer",
        ethnicity="Hispanic",
        notes=["Allergic to penicillin"],
        created_at=datetime.now(timezone.utc),
    )
    assert isinstance(patient.patient_id, uuid.UUID)
    assert isinstance(patient.created_at, datetime)
