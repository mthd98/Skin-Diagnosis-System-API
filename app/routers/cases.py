"""API Router for managing patient cases."""

import logging
from typing import List, Optional

from app.models.case import create_case
from app.models.case import get_case_by_id
from app.models.case import get_cases_by_doctor
from app.models.case import get_cases_by_patient
from app.models.doctor import get_current_doctor
from app.schema.case import Case
from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import Form
from fastapi import status
from fastapi import UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Initialize router and authentication scheme
router = APIRouter()
bearer_scheme = HTTPBearer()

# Configure logger
logger = logging.getLogger(__name__)


@router.post(
    "/new_case", response_model=Case, status_code=status.HTTP_201_CREATED
)
async def create_new_case(
    patient_number: int = Form(
        ..., description="The unique identifier assigned to the patient."
    ),
    case_notes: Optional[List[str]] = Form(
        default=[""],
        description="A list of notes or observations related to the diagnosis case. Defaults to an empty list.",
    ),
    file: UploadFile = File(
        ...,
        description="The medical image file (e.g., skin lesion image) uploaded for diagnosis.",
    ),
    current_doctor: dict = Depends(get_current_doctor),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    """Creates a new diagnosis case.

    Args:
        patient_number (int): The unique identifier of the patient for whom the case is being created.
        case_notes (Optional[List[str]]): Additional notes or observations related to the case. Defaults to an empty list.
        file (UploadFile): The image file associated with the diagnosis case (e.g., a medical image).
        current_doctor (dict): The authenticated doctor's details who is creating the case.

    Returns:
        JSONResponse: A JSON response containing the details of the newly created diagnosis case.

    Raises:
        HTTPException: 400 if input data is invalid or missing.
        HTTPException: 401 if the user is unauthorized or lacks necessary permissions.
        HTTPException: 500 if an internal server error occurs during case creation.
    """
    return await create_case(patient_number, case_notes, file, current_doctor)


@router.get("/cases/{case_id}", status_code=status.HTTP_200_OK)
def get_case(case_id: str,
             credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
    ):
    """Fetches a specific case by its unique ID.

    Args:
        case_id (str): The unique identifier of the case.

    Returns:
        JSONResponse: The requested case details.

    Raises:
        HTTPException: 404 if the case is not found.
        HTTPException: 500 if an internal server error occurs.
    """
    return get_case_by_id(case_id)


@router.get("/get_cases", status_code=status.HTTP_200_OK)
def get_doctor_cases(current_doctor: dict = Depends(get_current_doctor),
                     credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
    ):
    """Fetches all cases assigned to the authenticated doctor.

    Args:
        current_doctor (dict): Authenticated doctor.

    Returns:
        JSONResponse: List of cases assigned to the doctor.

    Raises:
        HTTPException: 500 if an internal server error occurs.
    """
    return get_cases_by_doctor(current_doctor)


@router.get("/cases/patient/{patient_id}", status_code=status.HTTP_200_OK)
def get_patient_cases(
    patient_id: str, current_doctor: dict = Depends(get_current_doctor),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    """Fetches all cases associated with a specific patient.

    Args:
        patient_id (str): The UUID of the patient.
        current_doctor (dict): Authenticated doctor.

    Returns:
        JSONResponse: List of cases associated with the patient.

    Raises:
        HTTPException: 404 if no cases are found.
        HTTPException: 500 if an internal server error occurs.
    """
    return get_cases_by_patient(patient_id)
