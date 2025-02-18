from datetime import datetime
from datetime import timezone
import os
import uuid

from app.db.MongoDB import MongoDBHandler
from app.schema.case import CaseCreate
from app.schema.case import DiagnosisResult
from app.schema.doctor import DoctorCreate
from app.schema.patient import PatientCreate
from pymongo import MongoClient
import pytest

# Load the test environment
load_dotenv(".env.test")


@pytest.fixture(scope="module")
def mongo_test_client():
    """Fixture to provide a test MongoDB client."""
    mongo_handler = MongoDBHandler()
    mongo_handler.connect()
    yield mongo_handler.client
    mongo_handler.disconnect()


@pytest.fixture(scope="module")
def test_database(mongo_test_client):
    """Fixture to create and clean up a test database."""
    test_db_name = os.getenv("DB_NAME", "test_skin_diagnosis_db")
    test_db = mongo_test_client[test_db_name]
    yield test_db
    mongo_test_client.drop_database(test_db_name)


@pytest.fixture(scope="function")
def test_collection(test_database):
    """Fixture to provide a clean test collection for each test."""
    collection = test_database["test_cases"]
    yield collection
    collection.delete_many({})


@pytest.fixture(scope="function")
def sample_doctor(test_database):
    """Fixture to insert a sample doctor into the test database."""
    doctor = DoctorCreate(
        name="Dr. John Doe",
        email="johndoe@example.com",
        password="hashedpassword",
    )
    doctor_dict = doctor.dict()
    doctor_dict["doctor_id"] = str(uuid.uuid4())
    doctor_dict["created_at"] = datetime.now(timezone.utc)
    test_database["test_doctors"].insert_one(doctor_dict)
    yield doctor_dict
    test_database["test_doctors"].delete_many({})


@pytest.fixture(scope="function")
def sample_patient(test_database):
    """Fixture to insert a sample patient into the test database."""
    patient = PatientCreate(
        patient_number=12345,
        name="Jane Doe",
        date_of_birth=datetime(1993, 5, 15, tzinfo=timezone.utc),
        gender="Female",
        country="USA",
        occupation="Teacher",
        ethnicity="Caucasian",
        notes=["No known allergies"],
    )
    patient_dict = patient.dict()
    patient_dict["patient_id"] = str(uuid.uuid4())
    patient_dict["created_at"] = datetime.now(timezone.utc)
    test_database["test_patients"].insert_one(patient_dict)
    yield patient_dict
    test_database["test_patients"].delete_many({})


@pytest.fixture(scope="function")
def sample_case(test_database, sample_doctor, sample_patient):
    """Fixture to insert a sample case associated with a patient and doctor."""
    case = CaseCreate(
        doctor_id=uuid.UUID(sample_doctor["doctor_id"]),
        patient_id=uuid.UUID(sample_patient["patient_id"]),
        diagnosis=DiagnosisResult(malignant=0.2, benign=0.8),
        notes="Routine check-up",
    )
    case_dict = case.dict()
    case_dict["case_id"] = str(uuid.uuid4())
    case_dict["created_at"] = datetime.now(timezone.utc)
    test_database["test_cases"].insert_one(case_dict)
    yield case_dict
    test_database["test_cases"].delete_many({})
