import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.config.db_init import db_handler
import uuid
import random
from datetime import datetime, timezone

# Create a test client
app = create_app()
client = TestClient(app)

# Fixture to handle MongoDB connection for tests
@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_db():
    db_handler.connect()   # Connect before running tests
    yield
    db_handler.disconnect()  # Disconnect after tests

# Helper function to generate unique emails and patient numbers
def generate_unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

def generate_unique_patient_number():
    return random.randint(10000000, 99999999)


# Test Data for Doctor and Patient
DOCTOR_DATA = {
    "name": "Dr. John Doe",
    "email": generate_unique_email(),
    "password": "securepassword123"
}

PATIENT_DATA = {
    "patient_number": generate_unique_patient_number(),
    "name": "Jane Smith",
    "date_of_birth": datetime(1990, 5, 20).isoformat(),
    "gender": "female",
    "country": "USA",
    "occupation": "Engineer",
    "ethnicity": "Caucasian",
    "notes": ["Diabetic", "Hypertension"]
}

# Test: Patient Registration Flow
def test_patient_registration_flow():
    # Step 1: Register Doctor
    reg_response = client.post("/users/register-doctor", json=DOCTOR_DATA)
    assert reg_response.status_code == 201, f"Unexpected status code: {reg_response.status_code}"

    # Step 2: Doctor Login
    login_data = {
        "email": DOCTOR_DATA["email"],
        "password": DOCTOR_DATA["password"]
    }
    login_response = client.post("/users/login", json=login_data)
    assert login_response.status_code == 200, f"Unexpected status code: {login_response.status_code}"
    token = login_response.json().get("access_token")
    assert token is not None

    # Step 3: Create New Patient
    create_patient_response = client.post(
        "/users/register-patient",  # Adjust the endpoint based on your routes
        headers={"Authorization": f"Bearer {token}"},
        json=PATIENT_DATA
    )
    assert create_patient_response.status_code == 201, f"Unexpected status code: {create_patient_response.status_code}"
    patient_number = create_patient_response.json().get("patient_number")
    assert patient_number is not None

    # Step 4: Get New Patient by patient_id
    get_patient_response = client.get(
        f"users/patients/{patient_number}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_patient_response.status_code == 200, f"Unexpected status code: {get_patient_response.status_code}"
    assert get_patient_response.json()["patient"]["patient_number"] == patient_number

if __name__ == "__main__":
    pytest.main()
