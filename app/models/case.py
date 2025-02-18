"""MongoDB model for skin diagnosis cases with image support."""

"""MongoDB model for skin diagnosis cases with image support."""

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

import gridfs
import requests
from fastapi import HTTPException, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pymongo.collection import Collection

from app.config import config as env
from app.config.db_init import db_handler
from app.models.api_key import get_api_key
from app.models.patient import get_patient_id
from app.schema.case import Case, DiagnosisResult
from app.schema.images import UploadImage

# Configure logger
logger = logging.getLogger(__name__)


def get_fs() -> gridfs.GridFS:
    """Initializes and returns a GridFS instance for handling large files.

    Returns:
        gridfs.GridFS: The GridFS instance connected to the Images database.
    """
    try:
        logger.info("Connecting to 'Images' database.")
        db = db_handler.get_database("Images")

        if db is None:
            logger.error(
                "Database connection failed: 'Images' database not found."
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed. 'Images' database not found.",
            )

        return gridfs.GridFS(db)

    except Exception as e:
        logger.exception(
            "Unexpected error during GridFS initialization: %s", str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error initializing GridFS.",
        )


def get_case_collection() -> Collection:
    """Retrieves the MongoDB case collection.

    Returns:
        Collection: The MongoDB collection for cases.
    """
    db = db_handler.get_collection(
        collection_name=env.get_cases_collection(), database="Cases"
    )

    if db is None:
        logger.error("Cases collection is unavailable.")
        raise Exception("Cases collection is unavailable.")

    logger.info("Successfully retrieved cases collection.")
    return db


def get_case_by_id(case_id: str) -> JSONResponse:
    """Retrieve a case from the database using its unique ID.

    Args:
        case_id (str): The unique identifier of the case.

    Returns:
        JSONResponse: The case details as a JSON response.
    """
    try:
        case = get_case_collection().find_one({"case_id": case_id}, {"_id": 0})

        if not case:
            logger.warning("Case with ID %s not found.", case_id)
            raise HTTPException(status_code=404, detail="Case not found")

        case_data = jsonable_encoder(Case(**case))
        logger.info("Successfully retrieved case ID: %s", case_id)

        return JSONResponse(content=case_data, status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("Error retrieving case ID %s: %s", case_id, str(e))
        raise HTTPException(status_code=500, detail="Error retrieving case.")


def get_cases_by_doctor(doctor: dict) -> JSONResponse:
    """Retrieve all cases assigned to a specific doctor.

    Args:
        doctor (dict): Doctor details.

    Returns:
        JSONResponse: A list of case documents.
    """
    try:
        doctor_id = doctor["doctor_id"]
        cases_cursor = get_case_collection().find(
            {"doctor_id": doctor_id}, {"_id": 0}
        )
        cases_list = list(cases_cursor)

        if not cases_list:
            logger.warning("No cases found for doctor ID %s.", doctor_id)
            return JSONResponse(
                content={"cases": []}, status_code=status.HTTP_200_OK
            )

        processed_cases = [
            jsonable_encoder(Case(**case)) for case in cases_list
        ]
        logger.info(
            "Retrieved %d case(s) for doctor ID: %s",
            len(processed_cases),
            doctor_id,
        )

        return JSONResponse(
            content={"cases": processed_cases}, status_code=status.HTTP_200_OK
        )

    except Exception as e:
        logger.exception("Error retrieving cases for doctor: %s", str(e))
        raise HTTPException(status_code=500, detail="Error retrieving cases.")


def generate_unique_filename(extension: str = "jpg") -> str:
    """Generates a unique filename.

    Args:
        extension (str): The file extension.

    Returns:
        str: A unique filename.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"image_{timestamp}_{unique_id}.{extension}"


async def get_diagnosis(file: bytes, api_key: str) -> DiagnosisResult:
    """Sends the uploaded image to the ML API for diagnosis.

    Args:
        file (bytes): The image file data.
        api_key (str): API key for authentication.

    Returns:
        DiagnosisResult: The diagnosis result.
    """
    try:
        headers = {"access_token": api_key}
        files = {"file": file}

        response = requests.post(
            env.get_ml_api_url(), files=files, timeout=30, headers=headers
        )
        logger.info("Received response from ML API: %s", response.status_code)

        if response.status_code != 200:
            logger.warning("ML API returned error: %s", response.text)
            raise HTTPException(
                status_code=response.status_code, detail="ML API error."
            )

        return response.json()

    except Exception as e:
        logger.exception("Error during diagnosis: %s", str(e))
        raise HTTPException(status_code=500, detail="Diagnosis error.")


def upload_case_image(image_data: UploadImage) -> str:
    """Uploads an image to GridFS.

    Args:
        image_data (UploadImage): The image data.

    Returns:
        str: The GridFS ID of the uploaded image.
    """
    try:
        if not image_data.image_bytes or not image_data.image_name:
            logger.warning("Invalid image input.")
            raise HTTPException(status_code=400, detail="Invalid image input.")

        fs = get_fs()
        image_id = fs.put(
            image_data.image_bytes, filename=image_data.image_name
        )
        logger.info("Image uploaded successfully with ID: %s", image_id)

        return str(image_id)

    except Exception as e:
        logger.exception("Error uploading image: %s", str(e))
        raise HTTPException(status_code=500, detail="Error uploading image.")


def get_case_image(image_id: str) -> bytes:
    """Retrieves an image from GridFS.

    Args:
        image_id (str): The GridFS ID of the image.

    Returns:
        bytes: The image file data.
    """
    try:
        fs = get_fs()
        image = fs.get(image_id)
        return image.read()

    except Exception as e:
        logger.exception("Error retrieving image: %s", str(e))
        raise HTTPException(status_code=500, detail="Error retrieving image.")


def get_cases_by_patient(patient_id: str) -> JSONResponse:
    """Retrieve all cases associated with a specific patient.

    Args:
        patient_id (str): The unique identifier of the patient.

    Returns:
        JSONResponse: A JSON response containing a list of cases associated with the patient.

    Raises:
        HTTPException: 404 if no cases are found for the patient.
        HTTPException: 500 if there is an error retrieving the cases.
    """
    try:
        cases_cursor = get_case_collection().find(
            {"patient_id": patient_id}, {"_id": 0}
        )
        cases_list = list(cases_cursor)

        if not cases_list:
            logger.warning("No cases found for patient ID %s.", patient_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No cases found for the given patient ID.",
            )

        logger.info(
            "Retrieved %d case(s) for patient ID: %s",
            len(cases_list),
            patient_id,
        )
        return JSONResponse(
            content={"cases": jsonable_encoder(cases_list)},
            status_code=status.HTTP_200_OK,
        )

    except HTTPException as http_exc:
        logger.error(
            "HTTPException while retrieving cases: %s", http_exc.detail
        )
        raise http_exc

    except Exception as e:
        logger.exception("Error retrieving cases for patient: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving cases.",
        )


async def create_case(
    patient_number: int,
    case_notes: Optional[List[str]],
    file: UploadFile,
    current_doctor: dict,
) -> JSONResponse:
    """Create a new diagnosis case by processing an uploaded image.

    Args:
        patient_number (int): The unique identifier of the patient.
        case_notes (Optional[List[str]]): Notes related to the case.
        file (UploadFile): The uploaded image file for diagnosis.
        current_doctor (dict): Information about the doctor submitting the case.

    Returns:
        JSONResponse: A JSON response containing the case details upon successful creation.

    Raises:
        HTTPException: 400 if invalid input is provided.
        HTTPException: 401 if authentication fails.
        HTTPException: 403 if the doctor does not have the necessary permissions.
        HTTPException: 404 if the patient is not found.
        HTTPException: 415 if the file format is unsupported.
        HTTPException: 500 if case creation fails.
    """
    try:
        logger.info(
            "Received request to create new case for patient_number: %s",
            patient_number,
        )

        # Validate file type
        allowed_extensions = (".png", ".jpg", ".jpeg")
        if not file.filename.lower().endswith(allowed_extensions):
            logger.error(
                "Unsupported file type: %s. Only PNG, JPG, and JPEG files are allowed.",
                file.filename,
            )
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file format '{file.filename}'. Allowed formats: PNG, JPG, JPEG.",
            )

        # Read file and generate a unique filename
        image_bytes = await file.read()
        unique_filename = generate_unique_filename(file.filename.split(".")[-1])
        image_data = UploadImage(
            image_bytes=image_bytes, image_name=unique_filename
        )

        # Validate doctor credentials
        doctor_id = current_doctor.get("doctor_id")
        if not doctor_id:
            logger.error("Unauthorized access: Missing doctor ID.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid doctor credentials.",
            )

        # Retrieve patient ID
        patient_id = get_patient_id(patient_number)
        if not patient_id:
            logger.warning("Patient not found: %s", patient_number)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found.",
            )

        # Upload the image to GridFS
        image_id = upload_case_image(image_data)
        logger.info(
            "Image uploaded successfully to GridFS with ID: %s", image_id
        )

        # Fetch doctor's API key for ML diagnosis
        doctor_api_key = get_api_key(doctor_id)
        if not doctor_api_key:
            logger.error("Doctor does not have a valid API key.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor API key missing or invalid.",
            )

        # Send the image for diagnosis using ML API
        diagnosis_result = await get_diagnosis(image_bytes, doctor_api_key)
        diagnosis = jsonable_encoder(diagnosis_result)

        # Prepare case data for storage
        case_data = {
            "case_id": str(uuid.uuid4()),
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "diagnosis": diagnosis["diagnosis"][0],
            "notes": case_notes if case_notes else [""],
            "image_id": image_id,
            "created_at": datetime.now(timezone.utc),
        }

        # Insert case data into MongoDB
        cases = get_case_collection()
        result = cases.insert_one(case_data)
        if not result.acknowledged:
            logger.error("Database insert for case not acknowledged.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database insert failed.",
            )

        logger.info(
            "Case created successfully with id: %s", case_data["case_id"]
        )
        case_data.pop("_id")
        logger.info("Case Data: %s", case_data)
        return JSONResponse(
            content={"status": "success", "case": jsonable_encoder(case_data)},
            status_code=status.HTTP_201_CREATED,
        )

    except HTTPException as http_exc:
        logger.error("HTTPException during case creation: %s", http_exc.detail)
        raise http_exc

    except Exception as e:
        logger.exception("Unexpected error creating case: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the case.",
        )
