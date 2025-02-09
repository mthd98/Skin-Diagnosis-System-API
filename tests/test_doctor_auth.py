import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.config.db_init import db_handler
import uuid

# Create a test client
app = create_app()
client = TestClient(app)

# Fixture to handle MongoDB connection for tests
@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_db():
    db_handler.connect()   # Connect before running tests
    yield
    db_handler.disconnect()  # Disconnect after tests

# Helper function to generate unique emails
def generate_unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

# Test Data
DOCTOR_DATA = {
    "name": "Dr. John Doe",
    "email": generate_unique_email(),
    "password": "securepassword123"
}

# Test: Doctor Registration
def test_doctor_registration():
    response = client.post("/users/register-doctor", json=DOCTOR_DATA)
    assert response.status_code == 201, f"Unexpected status code: {response.status_code}"
    assert response.json()["email"] == DOCTOR_DATA["email"]
    assert "doctor_id" in response.json()

# Test: Duplicate Doctor Registration (Invalid Case)
def test_duplicate_doctor_registration():
    client.post("/users/register-doctor", json=DOCTOR_DATA)  # Register the doctor first
    response = client.post("/users/register-doctor", json=DOCTOR_DATA)
    assert response.status_code == 400, f"Unexpected status code: {response.status_code}"
    assert response.json()["detail"] == "Email is already registered."

# Test: Doctor Login
def test_doctor_login():
    client.post("/users/register-doctor", json=DOCTOR_DATA)  # Ensure the doctor is registered
    login_data = {
        "email": DOCTOR_DATA["email"],
        "password": DOCTOR_DATA["password"]
    }
    response = client.post("/users/login", json=login_data)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    assert "access_token" in response.json()

# Test: Doctor Login with Wrong Password (Invalid Case)
def test_doctor_login_wrong_password():
    client.post("/users/register-doctor", json=DOCTOR_DATA)  # Ensure the doctor is registered
    login_data = {
        "email": DOCTOR_DATA["email"],
        "password": "wrongpassword"
    }
    response = client.post("/users/login", json=login_data)
    assert response.status_code == 401, f"Unexpected status code: {response.status_code}"
    assert response.json()["detail"] == "Invalid password."

if __name__ == "__main__":
    pytest.main()
