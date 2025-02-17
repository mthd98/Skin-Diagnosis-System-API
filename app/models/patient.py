"""MongoDB model for managing patient data."""

from datetime import date
from datetime import datetime
from datetime import timezone
import logging
import uuid

from app.config import config as env
from app.config.db_init import db_handler
from app.schema.patient import PatientCreate
from fastapi import HTTPException
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import pymongo
from pymongo.collection import Collection

# Configure logger
logger = logging.getLogger(__name__)


def get_patient_collection() -> Collection:
    """Retrieves the MongoDB patient collection.

    Returns:
        Collection: The MongoDB collection for patients.

    Raises:
        Exception: If the patient collection cannot be retrieved.
    """
    try:
        db = db_handler.get_collection(
            collection_name=env.get_patients_collection(), database="Users"
        )
        logger.info("Database: %s", env.get_patients_collection())
        if db is None:
            logger.error("Patient collection is unavailable.")
            raise Exception("Patient collection is unavailable.")

        logger.info("Successfully retrieved patient collection.")
        return db

    except Exception as e:
        logger.exception("Failed to retrieve patient collection: %s", str(e))
        raise


def create_patient(
    patient_info: PatientCreate, current_doctor: dict
) -> JSONResponse:
    """
    Creates a new patient profile in the database.

    Args:
        patient_info (PatientCreate): The validated patient details (including patient_number).
        current_doctor (dict): The currently logged-in doctor's details obtained via get_current_doctor.

    Returns:
        JSONResponse: A JSON response containing either the created patient object
                      or an error message.
    """
    try:
        logger.info("Creating patient profile for name: %s", patient_info.name)

        # Ensure doctor_id is present
        doctor_id = current_doctor.get("doctor_id") or current_doctor.get("id")
        if not doctor_id:
            error_message = "Current doctor does not have a valid identifier."
            logger.error(error_message)
            return JSONResponse(
                content={"status": "error", "message": error_message},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        # Retrieve patient collection
        patients: Collection = get_patient_collection()

        # Extract and normalize fields
        patient_number = patient_info.patient_number
        if not patient_number:
            raise ValueError("Patient number cannot be empty.")

        name = patient_info.name.strip().title()

        # Validate and Format Date of Birth (YYYY-MM-DD)
        try:
            if isinstance(patient_info.date_of_birth, date):
                date_of_birth = patient_info.date_of_birth.strftime(
                    "%Y-%m-%d"
                )  # ✅ Convert to YYYY-MM-DD string
            else:
                raise ValueError(
                    "Invalid date_of_birth format. Expected YYYY-MM-DD."
                )
        except Exception as dob_error:
            logger.error("Invalid date_of_birth: %s", str(dob_error))
            return JSONResponse(
                content={
                    "status": "error",
                    "message": "Invalid date_of_birth format. Expected YYYY-MM-DD.",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        gender = patient_info.gender.lower()
        country = patient_info.country.title() if patient_info.country else None
        occupation = (
            patient_info.occupation.title() if patient_info.occupation else None
        )
        ethnicity = (
            patient_info.ethnicity.title() if patient_info.ethnicity else None
        )
        notes = patient_info.notes if patient_info.notes else None

        # Check for duplicate patient_number
        if patients.find_one({"patient_number": patient_number}):
            error_message = f"Patient number {patient_number} already exists."
            logger.warning(error_message)
            return JSONResponse(
                content={"status": "error", "message": error_message},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Prepare patient data
        patient_data = {
            "patient_id": str(uuid.uuid4()),
            "patient_number": patient_number,
            "name": name,
            "date_of_birth": date_of_birth,  # ✅ Now formatted correctly
            "gender": gender,
            "country": country,
            "occupation": occupation,
            "ethnicity": ethnicity,
            "notes": notes,
            "created_at": datetime.now(timezone.utc),
        }

        # Insert into the database
        try:
            result = patients.insert_one(patient_data)
            if not result.acknowledged:
                raise pymongo.errors.OperationFailure(
                    "Database insert not acknowledged."
                )
        except pymongo.errors.PyMongoError as db_error:
            logger.error(
                "Database error while inserting patient: %s", str(db_error)
            )
            return JSONResponse(
                content={
                    "status": "error",
                    "message": "Database error occurred while creating the patient.",
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        patient_data.pop("_id", None)

        logger.info(
            "Patient created successfully with patient_number: %s",
            patient_data["patient_number"],
        )

        return JSONResponse(
            content=jsonable_encoder(patient_data),
            status_code=status.HTTP_201_CREATED,
        )

    except ValidationError as ve:
        # Extract field-specific validation errors
        errors = ve.errors()
        error_details = [
            {
                "field": err.get("loc", ["unknown"])[-1],
                "message": err.get("msg", "Invalid input"),
                "type": err.get("type", "validation_error"),
            }
            for err in errors
        ]
        logger.error("Validation error: %s", error_details)
        return JSONResponse(
            content={"status": "error", "errors": error_details},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    except ValueError as ve:
        logger.warning("Validation error: %s", str(ve))
        return JSONResponse(
            content={"status": "error", "message": str(ve)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except KeyError as ke:
        logger.error("Missing required data: %s", str(ke))
        return JSONResponse(
            content={
                "status": "error",
                "message": f"Missing required data: {str(ke)}",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        logger.exception("Unexpected error: %s", str(e))
        return JSONResponse(
            content={
                "status": "error",
                "message": "An unexpected error occurred.",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def get_all_patients() -> JSONResponse:
    """Retrieves all patient profiles.

    Returns:
        JSONResponse: A JSON response containing the list of patients.

    Raises:
        HTTPException: 500 if an error occurs while retrieving patients.
    """
    try:
        patients = get_patient_collection()

        patient_cursor = patients.find({}, {"_id": 0})
        patient_list = list(patient_cursor)

        if not patient_list:
            logger.info("No patients found in the database.")
            return JSONResponse(
                content={"message": "No patients found."},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return JSONResponse(
            content={"patients": jsonable_encoder(patient_list)},
            status_code=status.HTTP_200_OK,
        )

    except HTTPException as http_err:
        raise http_err

    except Exception as e:
        logger.exception("Unexpected error retrieving patients: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error retrieving patients.",
        )


def get_patient_by_patient_number(patient_number: int) -> JSONResponse:
    """Retrieves a patient by their patient number.

    Args:
        patient_number (int): The unique patient number.

    Returns:
        JSONResponse: A JSON response containing the patient object.

    Raises:
        HTTPException: 400 if the patient_number is invalid.
        HTTPException: 404 if the patient is not found.
        HTTPException: 500 if an error occurs during retrieval.
    """
    try:
        logger.info("Fetching patient with patient_number: %s", patient_number)

        # Validate patient_number
        if not isinstance(patient_number, int) or patient_number <= 0:
            logger.error("Invalid patient_number provided: %s", patient_number)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid patient number.",
            )

        patients = get_patient_collection()
        if patients is None:
            logger.error("Failed to connect to the patient collection.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error.",
            )

        # Query the database
        patient = patients.find_one(
            {"patient_number": patient_number}, {"_id": 0}
        )
        if not patient:
            logger.warning(
                "Patient with patient_number %s not found.", patient_number
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found.",
            )

        logger.info(
            "Patient found: %s (patient_number: %s)",
            patient["name"],
            patient_number,
        )
        return JSONResponse(
            content={"status": "success", "patient": jsonable_encoder(patient)},
            status_code=status.HTTP_200_OK,
        )

    except HTTPException as http_err:
        # Re-raise known HTTP exceptions
        raise http_err

    except TypeError:
        logger.error("Type error encountered when retrieving patient.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data format.",
        )

    except Exception as e:
        logger.exception("Unexpected error retrieving patient: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error retrieving patient.",
        )


def get_patient_id(patient_number: int) -> int:
    """Retrieves the patient_id using the patient_number.

    Args:
        patient_number (int): The unique patient number.

    Returns:
        str: The patient_id if found.

    Raises:
        HTTPException: 404 if the patient is not found.
        HTTPException: 500 if an error occurs during retrieval.
    """
    try:
        logger.info(
            "Fetching patient_id for patient_number: %s", patient_number
        )
        patients = get_patient_collection()

        patient = patients.find_one(
            {"patient_number": patient_number}, {"patient_id": 1, "_id": 0}
        )
        if not patient:
            logger.warning(
                "Patient with patient_number %s not found.", patient_number
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found.",
            )

        logger.info(
            "Patient ID found: %s for patient_number %s",
            patient["patient_id"],
            patient_number,
        )
        return patient["patient_id"]

    except Exception as e:
        logger.exception("Error retrieving patient_id: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving patient ID.",
        )
