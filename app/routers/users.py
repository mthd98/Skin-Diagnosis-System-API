"""User management routes with authentication and proper HTTP responses.

Note:
- Roles have been removed.
- Added doctor sign-up.
- Added patient registration (by doctors only).
- Added doctor sign-in.
- Improved error handling without shutting down the program.
- Added error logging.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.doctor import create_doctor, get_all_doctors, get_doctor_by_email, get_current_doctor
from app.models.patient import create_patient, get_patient_by_patient_number
from app.schema.doctor import DoctorCreate
from app.schema.patient import PatientCreate
from app.schema.authentication import LoginRequest
from app.utils.authentication import authenticate_doctor

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
bearer_scheme = HTTPBearer()

# -------- Doctor Registration --------

@router.post("/register-doctor", status_code=status.HTTP_201_CREATED)
def register_doctor(doctor_info: DoctorCreate):
    try:
        logger.info("Doctor registration input: %s", doctor_info.model_dump())
        
        existing_doctor = get_doctor_by_email(doctor_info.email)
        if existing_doctor:
            logger.error("Email is already registered: %s", doctor_info.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered."
            )
        
        # Pass a dictionary (not a JSON string) to create_doctor
        doctor_response = create_doctor(doctor_info)
        logger.info("Doctor successfully created.")
        return doctor_response

    except HTTPException as http_err:
        logger.error("Error creating doctor: %s", http_err.detail)
        raise http_err

    except Exception as e:
        logger.error("Error creating doctor: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating doctor: {str(e)}"
        )


# -------- Doctor Sign In --------

@router.post("/login", status_code=status.HTTP_200_OK)
def login(login_info: LoginRequest):
    """
    Endpoint to log in a doctor user.
    Delegates the entire login process to the model layer.

    Args:
        login_info (LoginRequest): The login data containing email and password.

    Returns:
        dict: A response containing the access token and token type on success,
              or an appropriate error message.
    """
    logger.info("Doctor Sign in input: %s", login_info.model_dump())
    
    return authenticate_doctor(login_info)
        
# -------- Patient Registration (By Doctor) --------

@router.post("/register-patient", status_code=status.HTTP_201_CREATED)
def register_patient(patient_in: PatientCreate, 
                     credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                     current_doctor: dict = Depends(get_current_doctor)
                     ):
    """
    Register a new patient.

    This endpoint requires a valid Authorization header with a Bearer token.
    The token is used to verify and extract the current doctor's details.
    
    Args:
        patient_in (PatientCreate): The validated patient registration data.
        current_doctor (dict): The current doctor's details obtained via the Bearer token.
    
    Returns:
        JSONResponse: The response generated by create_patient.
    """
    return create_patient(patient_in, current_doctor)


# -------- Get All Doctors (Admin Only) --------

@router.get("/doctors", status_code=status.HTTP_200_OK)
def get_doctors(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                current_doctor: dict = Depends(get_current_doctor)):
    """
    Route to retrieve all doctors.

    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token for authorization.
        current_doctor (dict): The current authenticated doctor information.

    Returns:
        dict: A dictionary containing the status and list of doctors.
    """
    return get_all_doctors()


# -------- Get Patients for Logged-in Doctor --------

# @router.get("/my-patients", status_code=status.HTTP_200_OK)
# def get_my_patients(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
#                 current_doctor: dict = Depends(get_current_doctor)
#                 ):
#     try:
#         patients = get_patients_by_doctor(current_doctor)
#         return {"status": "success", "patients": patients}

#     except Exception as e:
#         logger.error(f"Error retrieving patients: {str(e)}")
#         return {"status": "error", "message": f"Error retrieving patients: {str(e)}"}

@router.get("/patients/{patient_number}", status_code=status.HTTP_200_OK)
def get_patient(patient_number: int, 
                credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
                ):
    """
    API Endpoint to get a patient by patient number.
    """
    return get_patient_by_patient_number(patient_number)