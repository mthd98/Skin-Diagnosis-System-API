import logging
from fastapi import APIRouter, File, Form, HTTPException, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from app.models.patient import get_patient_id
from app.models.case import create_case, generate_unique_filename, get_case_by_id, get_cases_by_doctor, get_cases_by_patient, upload_case_image
from app.schema.case import Case
from app.schema.images import UploadImage
from app.models.doctor import get_current_doctor

router = APIRouter()
bearer_scheme = HTTPBearer()

# Configure logger
logger = logging.getLogger(__name__)

# -------- Create New Case (Accessible by Doctors & SuperUsers) -------- #
@router.post("/new_case", response_model=Case, status_code=status.HTTP_201_CREATED)
async def create_new_case(
    patient_number: int = Form(...),  # Patient's unique number from form-data.
    file: UploadFile = File(...),       # Uploaded image file from form-data.
    current_doctor: dict = Depends(get_current_doctor)  # Authenticated doctor details.
):
    """
    Create a new diagnosis case.

    Parameters:
        patient_number (int): Unique patient identifier.
        file (UploadFile): Image file to be processed.
        current_doctor (dict): Authenticated doctor's details.

    Returns:
        Case: The newly created diagnosis case details.
    """
    return await create_case(patient_number, file, current_doctor)

# -------- Get Case by ID (Accessible by Doctors & SuperUsers) -------- #
@router.get("/cases/{case_id}", status_code=status.HTTP_200_OK)
def get_case(case_id: str):
    """
    Endpoint to fetch a specific case by its unique ID.

    This endpoint delegates all logic to the model function `get_case_by_id`.
    The returned case is automatically converted to a JSON response.

    Args:
        case_id (str): The unique identifier of the case.

    Returns:
        JSONResponse: The requested case wrapped in a JSON response.
    """
    return get_case_by_id(case_id)

# -------- Get All Cases by Doctor (Accessible by Doctors & SuperUsers) -------- #
@router.get("/get_cases", status_code=status.HTTP_200_OK)
def get_doctor_cases(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_doctor: dict = Depends(get_current_doctor)
):
    """
    Fetches all cases assigned to a specific doctor.

    Args:
        doctor_id (str): The UUID of the doctor.
        credentials (HTTPAuthorizationCredentials): Bearer token for authentication.
        current_doctor (dict): Authenticated user with doctor role.

    Returns:
        JSONResponse: A JSON response containing the list of cases assigned to the doctor.
    """
    return get_cases_by_doctor(current_doctor)

# -------- Get All Cases by Patient (Accessible by Doctors, SuperUsers, and Patients) -------- #
@router.get("/cases/patient/{patient_id}", status_code=status.HTTP_200_OK)
def get_patient_cases(
    patient_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_doctor: dict = Depends(get_current_doctor)
):
    """
    Fetches all cases assigned to a specific patient.

    Args:
        patient_id (str): The UUID of the patient.
        credentials (HTTPAuthorizationCredentials): Bearer token for authentication.
        current_doctor (dict): Authenticated user with doctor role.

    Returns:
        JSONResponse: A JSON response containing the list of cases associated with the patient.
    """
    return get_cases_by_patient(patient_id)

