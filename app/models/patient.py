# models/patient.py

import uuid
import logging
import os
from datetime import datetime, timezone
from pymongo.collection import Collection
from fastapi import HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.config.db_init import db_handler
from app.schema.patient import PatientCreate
from app.models.doctor import get_current_doctor
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Use environment variables
PATIENTS_DB_COLLECTION = os.getenv("PATIENTS_DB_COLLECTION")

def get_patient_collection() -> Collection:
    """
    Retrieves the MongoDB patient collection.

    Returns:
        Collection: MongoDB collection for patient.

    Raises:
        Exception: If the patient collection cannot be retrieved.
    """
    try:
        db = db_handler.get_collection(
            collection_name=PATIENTS_DB_COLLECTION,
            database="Users"
        )
        if db is None:
            error_message = "Patient collection is unavailable."
            logging.error(error_message)
            raise Exception(error_message)
        logging.info("Got patient collection: %s", db)
        return db

    except Exception as e:
        logging.exception("Failed to retrieve patient collection: %s", str(e))
        raise

def create_patient(patient_info: PatientCreate, current_doctor: dict) -> JSONResponse:
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

        # Extract and normalize fields from the validated Pydantic model
        patient_number = patient_info.patient_number  # Supplied by the client
        name = patient_info.name.title()
        date_of_birth = patient_info.date_of_birth
        gender = patient_info.gender.lower()
        country = patient_info.country.title() if patient_info.country else None
        occupation = patient_info.occupation.title() if patient_info.occupation else None
        ethnicity = patient_info.ethnicity.title() if patient_info.ethnicity else None
        notes = patient_info.notes

        # Retrieve the doctor_id from the current doctor's details
        doctor_id = current_doctor.get("doctor_id") or current_doctor.get("id")
        if not doctor_id:
            error_message = "Current doctor does not have a valid identifier."
            logger.error(error_message)
            return JSONResponse(
                content={"status": "error", "message": error_message},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        # Retrieve the patient collection from the database
        patients: Collection = get_patient_collection()

        # Check for duplicate patient_number
        if patients.find_one({"patient_number": patient_number}):
            error_message = f"Patient number {patient_number} already exists."
            logger.warning(error_message)
            return JSONResponse(
                content={"status": "error", "message": error_message},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Prepare the patient data for insertion
        patient_data = {
            "patient_id": str(uuid.uuid4()),
            "patient_number": patient_number,
            "name": name,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "country": country,
            "occupation": occupation,
            "ethnicity": ethnicity,
            "notes": notes,
            "created_at": datetime.now(timezone.utc),
        }

        # Insert the patient record into the database
        result = patients.insert_one(patient_data)
        if not result.acknowledged:
            error_message = f"Database insert for patient {name} not acknowledged."
            logger.error(error_message)
            return JSONResponse(
                content={"status": "error", "message": error_message},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Remove the MongoDB _id from the output before returning
        patient_data.pop("_id", None)

        logger.info("Patient created successfully with patient_number: %s", patient_data["patient_number"])

        return JSONResponse(
            content=jsonable_encoder(patient_data),
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        logger.exception("An unexpected error occurred while creating patient: %s", str(e))
        return JSONResponse(
            content={"status": "error", "message": f"An error occurred while creating the patient: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# def get_patients_by_doctor(current_doctor: dict = Depends(get_current_doctor)) -> JSONResponse:
#     """
#     Retrieves all patients linked to the currently logged-in doctor.

#     Args:
#         current_doctor (dict): The currently logged-in doctor's details.

#     Returns:
#         JSONResponse: A JSON response containing a list of patient objects associated with the doctor.
#     """
#     try:
#         patients = get_patient_collection()
#         patient_cursor = patients.find({"doctor_id": current_doctor["id"]}, {"_id": 0})
#         patient_list = list(patient_cursor)
#         return JSONResponse(content={"patients": patient_list}, status_code=status.HTTP_200_OK)

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to retrieve patients: {str(e)}"
#         )

def get_all_patients() -> JSONResponse:
    """
    Retrieves all patient profiles linked to the currently logged-in doctor and returns them as JSON.

    Args:
        current_doctor (dict): The currently logged-in doctor's details.

    Returns:
        JSONResponse: A JSON response containing the list of patient profiles.
    """
    try:
        patients = get_patient_collection()
        patient_cursor = patients.find({"_id": 0})
        patient_list = list(patient_cursor)
        return JSONResponse(content={"patients": patient_list}, status_code=status.HTTP_200_OK)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve patients: {str(e)}"
        )

def get_patient_by_patient_number(patient_number: int) -> JSONResponse:
    """
    Retrieves a patient by their patient number for the currently logged-in doctor.

    Args:
        patient_number (int): The unique patient number.
        current_doctor (dict): The currently logged-in doctor's details.

    Returns:
        JSONResponse: A JSON response containing the patient object if found,
                      or an error message if not found.
    """
    try:
        logger.info(f"Fetching patient with patient_number: {patient_number}")

        # Retrieve the patient collection from the database
        patients: Collection = get_patient_collection()

        # Query the database for the patient with the given number linked to the current doctor
        patient = patients.find_one(
            {"patient_number": patient_number},
            {"_id": 0}  # Exclude the MongoDB internal _id field
        )

        if not patient:
            logger.warning(f"Patient with patient_number {patient_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with patient_number {patient_number} not found."
            )

        logger.info(f"Patient found: {patient['name']} (patient_number: {patient_number})")

        return JSONResponse(
            content={"status": "success", "patient": jsonable_encoder(patient)},
            status_code=status.HTTP_200_OK
        )

    except HTTPException as http_err:
        logger.error(f"Error retrieving patient: {http_err.detail}")
        raise http_err

    except Exception as e:
        logger.exception(f"An unexpected error occurred while retrieving patient: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the patient: {str(e)}"
        )

def get_patient_id(patient_number: int) -> str:
    """
    Retrieves the patient_id using the patient_number for the currently logged-in doctor.

    Parameters:
        patient_number (int): The unique patient number.
        current_doctor (dict): The currently logged-in doctor's details (must contain 'doctor_id').

    Returns:
        str: The patient_id if found.

    Raises:
        HTTPException: If the patient is not found or an unexpected error occurs.
    """
    try:
        logger.info(f"Fetching patient_id for patient_number: {patient_number}")

        # Retrieve the patient collection from the database.
        patients: Collection = get_patient_collection()

        # Query the database for the patient with the given number linked to the current doctor.
        patient = patients.find_one(
            {"patient_number": patient_number},
            {"patient_id": 1, "_id": 0}  # Only fetch the patient_id.
        )

        if not patient:
            logger.warning(
                f"Patient with patient_number {patient_number}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with patient_number {patient_number} not found."
            )

        logger.info(f"Patient ID found for patient_number {patient_number}: {patient['patient_id']}")
        return patient["patient_id"]

    except OverflowError:
        logger.error(f"Patient number {patient_number} exceeds 8-byte limit.")
        raise HTTPException(status_code=400, detail="Patient number exceeds the allowed range.")

    except HTTPException as http_err:
        logger.error(f"Error retrieving patient_id: {http_err.detail}")
        raise http_err

    except Exception as e:
        logger.exception(f"An unexpected error occurred while retrieving patient_id: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the patient_id: {str(e)}"
        )
