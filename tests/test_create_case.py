import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.config.db_init import db_handler
import uuid
from datetime import datetime
from io import BytesIO

# Setup FastAPI client
app = create_app()
client = TestClient(app)

# MongoDB setup for tests
@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_db():
    db_handler.connect()
    yield
    db_handler.disconnect()

# Helper functions
def generate_unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

def generate_unique_patient_number():
    return uuid.uuid4().int >> 64  # Generates a large, unique patient number

# Test Data
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

# Test: Create Case
def test_create_case():
    # Step 1: Register Doctor
    reg_response = client.post("/users/register-doctor", json=DOCTOR_DATA)
    assert reg_response.status_code == 201, f"Unexpected status code: {reg_response.status_code}"

    # Step 2: Doctor Login
    login_response = client.post(
        "/users/login",
        json={"email": DOCTOR_DATA["email"], "password": DOCTOR_DATA["password"]}
    )
    assert login_response.status_code == 200, f"Unexpected status code: {login_response.status_code}"
    token = login_response.json().get("access_token")
    assert token is not None

    # Step 3: Register Patient
    create_patient_response = client.post(
        "/users/register-patient",
        headers={"Authorization": f"Bearer {token}"},
        json=PATIENT_DATA
    )
    assert create_patient_response.status_code == 201, f"Unexpected status code: {create_patient_response.status_code}"
    patient_number = create_patient_response.json().get("patient_number")
    assert patient_number is not None

    # Step 4: Create Case with Image Data using form-data
    image_content = BytesIO(b"test_image_content")
    image_bytes = image_content.getvalue()

    create_case_response = client.post(
        "/cases/new_case",  # Ensure this matches your route definition
        headers={"Authorization": f"Bearer {token}"},
        data={"patient_number": patient_number},  # Send patient_number as form field
        files={"file": ("test_image.jpg", image_bytes, "image/jpeg")}  # Send file in multipart/form-data
    )

    assert create_case_response.status_code == 201, f"Unexpected status code: {create_case_response.status_code}"
    response_json = create_case_response.json()
    assert "case" in response_json, "Response JSON should contain a 'case' key"
    
    # Optionally, check some details in the returned case.
    case = response_json["case"]
    assert "case_id" in case, "Case should contain an 'id'"
    assert case.get("patient_id") is not None, "Case should contain a patient_id"

if __name__ == "__main__":
    pytest.main()
