import json

from app.schema.api_key import APIKey
from app.schema.case import Case
from app.schema.case import DiagnosisResult
from app.schema.doctor import DoctorCreate
from app.schema.doctor import DoctorDB
from app.schema.patient import Patient
from app.schema.patient import PatientCreate
from pydantic import ValidationError
import pytest


@pytest.mark.order(1)
def test_doctor_serialization():
    """Test serializing and deserializing a DoctorCreate object."""
    doctor_data = {
        "name": "Dr. Jane Doe",
        "email": "jane@example.com",
        "password": "securepass",
    }
    doctor = DoctorCreate(**doctor_data)
    serialized = doctor.model_dump_json()
    deserialized = DoctorCreate.model_validate_json(serialized)

    assert deserialized.name == "Dr. Jane Doe"
    assert deserialized.email == "jane@example.com"
    assert deserialized.password == "securepass"


@pytest.mark.order(2)
def test_patient_serialization():
    """Test serializing and deserializing a PatientCreate object."""
    patient_data = {
        "patient_number": 12345,
        "name": "John Doe",
        "date_of_birth": "1985-08-25T00:00:00",
        "gender": "Male",
        "country": "UK",
        "occupation": "Engineer",
        "ethnicity": "Hispanic",
        "notes": ["Allergic to penicillin"],
    }
    patient = PatientCreate(**patient_data)
    serialized = patient.model_dump_json()
    deserialized = PatientCreate.model_validate_json(serialized)

    assert deserialized.name == "John Doe"
    assert deserialized.patient_number == 12345
    assert deserialized.gender == "Male"


@pytest.mark.order(3)
def test_case_serialization():
    """Test serializing and deserializing a Case object."""
    case_data = {
        "doctor_id": "550e8400-e29b-41d4-a716-446655440000",
        "patient_id": "550e8400-e29b-41d4-a716-446655440001",
        "diagnosis": {"malignant": 0.8, "benign": 0.2},
        "notes": ["Suspicious mole detected", "Follow-up required"],
        "case_id": "550e8400-e29b-41d4-a716-446655440002",
        "created_at": "2023-10-10T00:00:00",
    }
    case = Case(**case_data)
    serialized = case.model_dump_json()
    deserialized = Case.model_validate_json(serialized)

    assert deserialized.notes == [
        "Suspicious mole detected",
        "Follow-up required",
    ]
    assert deserialized.diagnosis.malignant == 0.8


@pytest.mark.order(4)
def test_api_key_serialization():
    """Test serializing and deserializing an APIKey object."""
    api_key_data = {
        "api_key": "test_api_key",
        "expired_date": "2024-12-31T23:59:59",
    }
    api_key = APIKey(**api_key_data)
    serialized = api_key.model_dump_json()  # Use Pydantic V2 method
    deserialized = APIKey.model_validate_json(
        serialized
    )  # Use updated deserialization method

    assert deserialized.api_key == "test_api_key"
    assert deserialized.expired_date.isoformat() == "2024-12-31T23:59:59"


@pytest.mark.order(5)
def test_doctor_db_serialization():
    """Test serializing and deserializing a DoctorDB object."""
    doctor_data = {
        "doctor_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Dr. Jane Doe",
        "email": "jane@example.com",
        "created_at": "2023-10-10T00:00:00",
    }
    doctor = DoctorDB(**doctor_data)
    serialized = doctor.model_dump_json()
    deserialized = DoctorDB.model_validate_json(serialized)

    assert deserialized.name == "Dr. Jane Doe"
    assert deserialized.email == "jane@example.com"
