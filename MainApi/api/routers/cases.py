from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from api.models.cases import create_case, get_case_by_id, get_cases_by_doctor, get_cases_by_patient
from api.schema.cases import CaseCreate, CaseDB
from api.utils.authentication import require_role

router = APIRouter()

# -------- Create New Case (Accessible by Doctors & SuperUsers) -------- #

@router.post("/cases", response_model=CaseDB, status_code=status.HTTP_201_CREATED)
def create_new_case(
    case_in: CaseCreate,
    current_user: dict = Depends(require_role(["doctor", "superuser"]))
):
    """Creates a new diagnosis case.

    Args:
        case_in (CaseCreate): The case data.
        current_user (dict): Authenticated user with doctor or superuser role.

    Returns:
        CaseDB: The created case details.
    """
    case_data = create_case(
        doctor_id=case_in.doctor_id,
        patient_id=case_in.patient_id,
        diagnosis=case_in.diagnosis,
        notes=case_in.notes
    )
    return CaseDB(**case_data)

# -------- Get Case by ID (Accessible by Doctors & SuperUsers) -------- #

@router.get("/cases/{case_id}", response_model=CaseDB, status_code=status.HTTP_200_OK)
def get_case(
    case_id: str,
    current_user: dict = Depends(require_role(["doctor", "superuser"]))
):
    """Fetches a specific case by UUID.

    Args:
        case_id (str): The UUID of the case.
        current_user (dict): Authenticated user with doctor or superuser role.

    Returns:
        CaseDB: The requested case.
    """
    case = get_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseDB(**case)

# -------- Get All Cases by Doctor (Accessible by Doctors & SuperUsers) -------- #

@router.get("/cases/doctor/{doctor_id}", response_model=List[CaseDB], status_code=status.HTTP_200_OK)
def get_doctor_cases(
    doctor_id: str,
    current_user: dict = Depends(require_role(["doctor", "superuser"]))
):
    """Fetches all cases assigned to a specific doctor.

    Args:
        doctor_id (str): The UUID of the doctor.
        current_user (dict): Authenticated user with doctor or superuser role.

    Returns:
        List[CaseDB]: A list of cases.
    """
    return get_cases_by_doctor(doctor_id)

# -------- Get All Cases by Patient (Accessible by Doctors, SuperUsers, and Patients) -------- #

@router.get("/cases/patient/{patient_id}", response_model=List[CaseDB], status_code=status.HTTP_200_OK)
def get_patient_cases(
    patient_id: str,
    current_user: dict = Depends(require_role(["doctor", "superuser", "patient"]))
):
    """Fetches all cases assigned to a specific patient.

    Args:
        patient_id (str): The UUID of the patient.
        current_user (dict): Authenticated user with doctor, superuser, or patient role.

    Returns:
        List[CaseDB]: A list of cases.
    """
    return get_cases_by_patient(patient_id)
