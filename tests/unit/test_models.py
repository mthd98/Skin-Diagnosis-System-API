from datetime import datetime
from datetime import timezone
import json
import random
import uuid

from app.models.api_key import allocate_api_key
from app.models.api_key import get_api_key
from app.models.api_key import get_api_key_collection
from app.models.case import get_case_by_id
from app.models.case import get_case_collection
from app.models.case import get_cases_by_doctor
from app.models.case import get_cases_by_patient
from app.models.doctor import create_doctor
from app.models.doctor import get_all_doctors
from app.models.doctor import get_doctor_by_email
from app.models.doctor import get_doctor_by_id
from app.models.patient import create_patient
from app.models.patient import get_all_patients
from app.models.patient import get_patient_by_patient_number
from app.models.patient import get_patient_id
from app.schema.doctor import DoctorCreate
from app.schema.patient import PatientCreate
import pytest


def generate_unique_email():
    """Generates a unique email using a UUID."""
    return f"testdoctor_{uuid.uuid4().hex[:8]}@example.com"


def generate_unique_patient_number():
    """Generates a unique 8-digit patient number."""
    return random.randint(10000000, 99999999)


# Fixture to create a new doctor with a unique email for each test run.
@pytest.fixture(scope="module")
def new_doctor():
    email = generate_unique_email()
    doctor_info = {
        "name": "Dr. Test",
        "email": email,
        "password": "securepassword",
    }
    response = create_doctor(DoctorCreate(**doctor_info))
    # Verify creation via status code
    assert response.status_code == 201
    doctor = get_doctor_by_email(email)
    if hasattr(doctor, "body"):
        doctor = json.loads(doctor.body.decode("utf-8"))
    assert doctor is not None
    return doctor


# Fixture to create a new patient with a unique patient number for each test run.
@pytest.fixture(scope="module")
def new_patient(new_doctor):
    patient_number = generate_unique_patient_number()
    patient_info = {
        "patient_number": patient_number,
        "name": "John Doe",
        "date_of_birth": datetime(1985, 8, 25, tzinfo=timezone.utc),
        "gender": "Uk",  # Adjust as needed (e.g., "UK")
        "occupation": "Engineer",
        "ethnicity": "Hispanic",
        "notes": ["Allergic to penicillin"],
    }
    response = create_patient(
        PatientCreate(**patient_info), {"doctor_id": new_doctor["doctor_id"]}
    )
    assert response.status_code == 201
    patient = get_patient_by_patient_number(patient_number)
    if hasattr(patient, "body"):
        patient = json.loads(patient.body.decode("utf-8"))
    assert patient is not None
    return patient


@pytest.mark.order(1)
def test_allocate_api_key():
    """Test allocating an API key for a doctor."""
    doctor_id = str(uuid.uuid4())
    api_key = allocate_api_key(doctor_id)
    assert isinstance(api_key, str)

    api_keys = get_api_key_collection()
    stored_key = api_keys.find_one({"doctor_id": doctor_id})
    assert stored_key is not None
    assert stored_key["api_key"] == api_key


@pytest.mark.order(2)
def test_get_api_key():
    """Test retrieving an API key for a doctor."""
    doctor_id = str(uuid.uuid4())
    allocate_api_key(doctor_id)
    retrieved_key = get_api_key(doctor_id)
    assert isinstance(retrieved_key, str)


@pytest.mark.order(3)
def test_create_doctor(new_doctor):
    """Test creating a new doctor using a unique email."""
    # new_doctor fixture creates a doctor with a unique email.
    assert new_doctor["name"] == "Dr. Test"


@pytest.mark.order(4)
def test_get_doctor_by_id(new_doctor):
    """Test retrieving a doctor by ID."""
    doctor_id = new_doctor["doctor_id"]
    retrieved_doctor = get_doctor_by_id(doctor_id)
    if hasattr(retrieved_doctor, "body"):
        retrieved_doctor = json.loads(retrieved_doctor.body.decode("utf-8"))
    assert retrieved_doctor is not None
    assert retrieved_doctor["email"] == new_doctor["email"]


@pytest.mark.order(5)
def test_get_all_doctors():
    """Test retrieving all doctors."""
    response = get_all_doctors()
    assert response.status_code == 200
    data = json.loads(response.body.decode("utf-8"))
    assert isinstance(data["doctors"], list)


@pytest.mark.order(6)
def test_create_patient(new_patient):
    """Test creating a new patient using a unique patient number."""
    # Assuming the patient data is nested under "patient"
    assert new_patient["patient"]["name"] == "John Doe"


@pytest.mark.order(7)
def test_get_patient_id(new_patient):
    """Test retrieving a patient ID by patient number."""
    # Use the nested structure: patient_number is inside new_patient["patient"]
    patient_number = new_patient["patient"]["patient_number"]
    patient_id = get_patient_id(patient_number)
    assert isinstance(patient_id, (int, str))


@pytest.mark.order(8)
def test_get_all_patients():
    """Test retrieving all patients."""
    response = get_all_patients()
    assert response.status_code == 200
    data = json.loads(response.body.decode("utf-8"))
    assert isinstance(data["patients"], list)


@pytest.mark.order(9)
def test_get_case_by_id(new_doctor, new_patient):
    """Test retrieving a case by its ID."""
    cases = get_case_collection()
    test_case = {
        "case_id": str(uuid.uuid4()),
        "doctor_id": new_doctor["doctor_id"],
        # Access patient_id from the nested dictionary.
        "patient_id": new_patient["patient"]["patient_id"],
        "diagnosis": {"malignant": 0.8, "benign": 0.2},
        "notes": ["Follow-up required"],
        "created_at": datetime.now(timezone.utc),
    }
    cases.insert_one(test_case)

    response = get_case_by_id(test_case["case_id"])
    assert response.status_code == 200
    data = json.loads(response.body.decode("utf-8"))
    # Assuming the response returns a key "case" with the test case data.
    assert data["notes"] == ["Follow-up required"]

    # Cleanup: remove the test case.
    cases.delete_one({"case_id": test_case["case_id"]})


@pytest.mark.order(10)
def test_get_cases_by_doctor(new_doctor):
    """Test retrieving cases assigned to a doctor."""
    response = get_cases_by_doctor(new_doctor)
    assert response.status_code == 200
    data = json.loads(response.body.decode("utf-8"))
    assert isinstance(data["cases"], list)


@pytest.mark.order(11)
def test_get_cases_by_patient(new_patient):
    """Test retrieving cases assigned to a patient."""
    # Insert a test case for the patient to ensure at least one case exists.
    cases = get_case_collection()
    test_case = {
        "case_id": str(uuid.uuid4()),
        "doctor_id": new_patient["patient"].get("doctor_id", "dummy"),
        "patient_id": new_patient["patient"]["patient_id"],
        "diagnosis": {"malignant": 0.9, "benign": 0.1},
        "notes": ["Test case for get_cases_by_patient"],
        "created_at": datetime.now(timezone.utc),
    }
    cases.insert_one(test_case)

    response = get_cases_by_patient(new_patient["patient"]["patient_id"])
    assert response.status_code == 200
    data = json.loads(response.body.decode("utf-8"))
    assert isinstance(data["cases"], list)
    # Ensure the inserted test case is present.
    assert any(
        case["case_id"] == test_case["case_id"] for case in data["cases"]
    )

    # Cleanup: remove the test case.
    cases.delete_one({"case_id": test_case["case_id"]})
