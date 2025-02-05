"""Case management routes with image upload support."""

import uuid
from fastapi import APIRouter, HTTPException, Depends, Response, UploadFile, File, status
from typing import List
from models.cases import create_case, get_case_by_id, get_cases_by_doctor, get_cases_by_patient, upload_case_image, get_case_image
from schema.cases import CaseCreate, CaseDB

router = APIRouter()

@router.post("/cases", response_model=CaseDB, status_code=status.HTTP_201_CREATED)
async def create_new_case(case_in: CaseCreate, file: UploadFile = File(None)):
    """Creates a new diagnosis case with optional image upload.

    Args:
        case_in (CaseCreate): The case data.
        file (UploadFile, optional): The uploaded image file.

    Returns:
        CaseDB: The created case details.
    """
    
    image_id = None
    try:
        if file:
            image_id = upload_case_image(await file.read(), file.filename)

        case_data = create_case(
            doctor_id=case_in.doctor_id,
            patient_id=case_in.patient_id,
            diagnosis=case_in.diagnosis,
            notes=case_in.notes,
            image_id=image_id
        )

        return CaseDB(**case_data, image_url=f"/cases/image/{image_id}" if image_id else None)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No image uploaded.")
    
@router.get("/cases/image/{image_id}", status_code=status.HTTP_200_OK)
async def get_case_image_endpoint(image_id: str):
    """Fetches an uploaded case image.

    Args:
        image_id (str): The GridFS ID of the image.

    Raises:
        HTTPException 404: If the image is not found.

    Returns:
        Response: The image file.
    """
    try:
        image_data = get_case_image(image_id)
        return Response(content=image_data, media_type="image/jpeg")
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")

@router.get("/cases/{case_id}", response_model=CaseDB, status_code=status.HTTP_200_OK)
def get_case(case_id: str):
    """Fetches a specific case by UUID.

    Args:
        case_id (str): The UUID of the case.

    Raises:
        HTTPException 400: If UUID format is invalid.
        HTTPException 404: If the case is not found.

    Returns:
        CaseDB: The requested case.
    """
    try:
        uuid.UUID(case_id)  # Validate UUID format
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format."
        )

    case = get_case_by_id(case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found."
        )
    
    image_url = f"/cases/image/{case['image_id']}" if case.get("image_id") else None
    return CaseDB(**case, image_url=image_url)
