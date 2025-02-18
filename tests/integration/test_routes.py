from io import BytesIO
import random
import uuid

from app.main import app
from fastapi.testclient import TestClient
from PIL import Image
import pytest

client = TestClient(app)


def generate_unique_email():
    return f"testdoctor_{uuid.uuid4().hex[:8]}@example.com"


def generate_unique_patient_number():
    return random.randint(10000000, 99999999)


@pytest.fixture(scope="session")
def unique_doctor():
    return {
        "name": "Dr. Test",
        "email": generate_unique_email(),
        "password": "securepassword",
    }


@pytest.mark.order(1)
def test_register_doctor(unique_doctor):
    response = client.post("/users/register-doctor", json=unique_doctor)
    assert response.status_code in [
        200,
        201,
    ], f"Unexpected response: {response.json()}"


@pytest.mark.order(2)
def test_login_doctor(unique_doctor):
    response = client.post(
        "/users/login",
        json={
            "email": unique_doctor["email"],
            "password": unique_doctor["password"],
        },
    )
    assert (
        response.status_code == 200
    ), f"Unexpected response: {response.json()}"


@pytest.fixture(scope="function")
def auth_token(unique_doctor):
    auth_response = client.post(
        "/users/login",
        json={
            "email": unique_doctor["email"],
            "password": unique_doctor["password"],
        },
    )
    return auth_response.json().get("access_token")


@pytest.fixture(scope="session")
def unique_patient():
    return {
        "patient_number": generate_unique_patient_number(),
        "name": "Jane Doe",
        "date_of_birth": "1993-05-15",
        "gender": "Female",
        "country": "USA",
        "occupation": "Teacher",
        "ethnicity": "Caucasian",
        "notes": ["No known allergies"],
    }


@pytest.mark.order(3)
def test_register_patient(auth_token, unique_patient):
    response = client.post(
        "/users/register-patient",
        json=unique_patient,
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code in [
        200,
        201,
    ], f"Unexpected response: {response.json()}"


@pytest.mark.order(4)
def test_get_all_doctors(auth_token):
    response = client.get(
        "/users/doctors", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert (
        response.status_code == 200
    ), f"Unexpected response: {response.json()}"
    assert isinstance(response.json().get("doctors"), list)


@pytest.mark.order(5)
def test_get_patient_by_number(auth_token, unique_patient):
    response = client.get(
        f"/users/patients/{unique_patient['patient_number']}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Unexpected response: {response.json()}"
    patient_data = response.json().get("patient", {})
    assert (
        patient_data.get("name") == "Jane Doe"
    ), f"Unexpected patient data: {patient_data}"


@pytest.mark.order(6)
def test_create_new_case(auth_token, unique_patient):
    """Test creating a new medical case using an actual image file."""
    # Open the actual image file in binary mode.
    # Ensure that tests/assets/test_image.jpg exists and is a valid JPEG.
    with open("tests/data/test_image.jpeg", "rb") as f:
        valid_image_bytes = f.read()

    response = client.post(
        "/cases/new_case",
        data={
            "patient_number": unique_patient["patient_number"],
            "case_notes": "Follow-up required",
        },
        files={"file": ("test_image.jpg", valid_image_bytes, "image/jpeg")},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code in [
        200,
        201,
    ], f"Unexpected response: {response.json()}"
