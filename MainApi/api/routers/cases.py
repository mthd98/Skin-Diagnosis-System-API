# Defines routes and endpoints related to cases.
import uuid
from typing import Any
from fastapi import APIRouter, HTTPException
from api.models.cases import *
router = APIRouter(prefix="/cancer", tags=["cancer"])

# Make diagnosis

# TODO: Validate API key and get doctor ID

# TODO: Get case histories -> get all cases in database 

# TODO: Get case doctor histories -> get all cases related to the doctor -> use Doctor_id

# TODO: Get patient cases-> get all cases related to a patient -> use Doctor_id and Patient_id

# TODO: Get case -> get case by case_ID and Doctor_id
@router.get("/{id}", response_model=UserCaseResponse)
def read_item(session , current_user: CaseRequest, Doctor_id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    item = session.get(UserCaseResponse, id)
    if not item:
        raise HTTPException(status_code=404, detail="Case not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item
