"""User management routes with authentication and proper HTTP responses."""

import logging

from app.models.doctor import create_doctor
from app.models.doctor import get_all_doctors
from app.models.doctor import get_current_doctor
from app.models.patient import create_patient
from app.models.patient import get_patient_by_patient_number
from app.schema.authentication import LoginRequest
from app.schema.doctor import DoctorCreate
from app.schema.patient import PatientCreate
from app.utils.authentication import authenticate_doctor
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
bearer_scheme = HTTPBearer()

# -------- Doctor Registration --------


@router.post("/register-doctor", status_code=status.HTTP_201_CREATED)
def register_doctor(doctor_info: DoctorCreate):
    """
    Registers a new doctor.

    Args:
        doctor_info (DoctorCreate): The validated doctor registration data.

    Returns:
        JSONResponse: A response indicating success or failure.
    """
    return create_doctor(doctor_info)


# -------- Doctor Sign In --------


@router.post("/login", status_code=status.HTTP_200_OK)
def login(login_info: LoginRequest):
    """
    Endpoint to log in a doctor user.

    Args:
        login_info (LoginRequest): The login data containing email and password.

    Returns:
        dict: A response containing the access token and token type on success.
    """
    return authenticate_doctor(login_info)


# -------- Patient Registration (By Doctor) --------


@router.post("/register-patient", status_code=status.HTTP_201_CREATED)
def register_patient(
    patient_in: PatientCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_doctor: dict = Depends(get_current_doctor),
):
    """
    Register a new patient.

    Args:
        patient_in (PatientCreate): The validated patient registration data.
        credentials (HTTPAuthorizationCredentials): Bearer token for authentication.
        current_doctor (dict): The current doctor's details.

    Returns:
        JSONResponse: The response generated by create_patient.
    """
    return create_patient(patient_in, current_doctor)


# -------- Get All Doctors (Admin Only) --------


@router.get("/doctors", status_code=status.HTTP_200_OK)
def get_doctors(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    """
    Route to retrieve all doctors.

    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token for authorization.
        current_doctor (dict): The current authenticated doctor information.

    Returns:
        dict: A dictionary containing the status and list of doctors.
    """
    return get_all_doctors()


# -------- Get a Patient by Patient Number --------


@router.get("/patients/{patient_number}", status_code=status.HTTP_200_OK)
def get_patient(
    patient_number: int,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """
    API Endpoint to get a patient by patient number.

    Args:
        patient_number (int): The unique identifier of the patient.
        credentials (HTTPAuthorizationCredentials): Bearer token for authentication.

    Returns:
        JSONResponse: The requested patient details.
    """
    return get_patient_by_patient_number(patient_number)
