import uuid
import logging
import os
from datetime import datetime, timezone
from pymongo.collection import Collection
from fastapi import Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.schema.doctor import DoctorCreate, DoctorProfile, APIKey
from app.utils.authentication import hash_password, verify_token
from app.config.db_init import db_handler
from app.models.api_key import allocate_api_key, get_api_key
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Use environment variables
DOCTORS_DB_COLLECTION = os.getenv("DOCTORS_DB_COLLECTION")


def get_doctor_collection() -> Collection:
    """
    Retrieves the MongoDB doctor collection.

    Returns:
        Collection: MongoDB collection for doctors.

    Raises:
        Exception: If the doctor collection cannot be retrieved.
    """
    try:
        db = db_handler.get_collection(
            collection_name=DOCTORS_DB_COLLECTION,
            database="Users"
        )
        if db is None:
            error_message = "Doctor collection is unavailable."
            logging.error(error_message)
            raise Exception(error_message)
        logging.info("Got doctor collection: %s", db)
        return db

    except Exception as e:
        logging.exception("Failed to retrieve doctor collection: %s", str(e))
        raise

def create_doctor(doctor_info: DoctorCreate) -> JSONResponse:
    """
    Creates a new doctor in the database.

    Args:
        doctor_info (DoctorCreate): The validated doctor details.

    Returns:
        JSONResponse: A JSON response containing either the created doctor object (with the password removed)
                      or an error message.
    """
    try:
        logger.info("Creating doctor profile for email: %s", doctor_info.email)

        # Extract fields from the validated Pydantic model.
        email = doctor_info.email.lower()
        name = doctor_info.name.title()
        password_raw = doctor_info.password

        # Retrieve the doctor collection from the database.
        doctors: Collection = get_doctor_collection()

        # Hash the password.
        password = hash_password(password_raw)

        # Prepare the doctor data for insertion.
        doctor_data = {
            "doctor_id": str(uuid.uuid4()),
            "email": email,
            "name": name,
            "password": password,
            "created_at": datetime.now(timezone.utc),
        }

        # Insert the doctor record into the database.
        result = doctors.insert_one(doctor_data)
        if not result.acknowledged:
            error_message = f"Database insert for doctor {email} not acknowledged."
            logger.error(error_message)
            return JSONResponse(
                content={"status": "error", "message": error_message},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Allocate the API key after doctor creation
        api_key = allocate_api_key(doctor_data["doctor_id"])

        # Remove sensitive fields before returning the response
        doctor_data.pop("password", None)
        doctor_data.pop("_id", None)
        doctor_data["api_key"] = api_key  # Include the allocated API key in the response

        
        logger.info("Doctor created successfully with id: %s", doctor_data["doctor_id"])

        return JSONResponse(
            content=jsonable_encoder(doctor_data),
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        logger.exception("An unexpected error occurred while creating doctor: %s", str(e))
        return JSONResponse(
            content={"status": "error", "message": f"An error occurred while creating the doctor: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

def get_doctor_by_id(doctor_id: str) -> dict:
    """
    Retrieves a doctor by their UUID.

    Args:
        doctor_id (str): The UUID string of the doctor.

    Returns:
        dict: The doctor object, if found.
    """
    doctors = get_doctor_collection()
    return doctors.find_one({"doctor_id": doctor_id}, {"_id": 0, "password": 0})

def get_all_doctors() -> JSONResponse:
    """
    Retrieves all doctors from the database.

    Returns:
        JSONResponse: A JSON response containing a list of doctor objects (with _id and password excluded)
                      and an HTTP 200 status code.
    """
    try:
        doctors = get_doctor_collection()
        # Retrieve all doctors and exclude the Mongo _id and password fields from the result.
        doctor_cursor = doctors.find({}, {"_id": 0, "password": 0})
        doctor_list = list(doctor_cursor)
        return JSONResponse(content={"doctors": jsonable_encoder(doctor_list)}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.exception("Failed to retrieve doctors: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve doctors: {str(e)}"
        )

def get_doctor_by_email(email: str) -> dict:
    """
    Retrieves a doctor from the database using their email address.

    Args:
        email (str): The email address of the doctor.

    Returns:
        dict: The doctor object if found, otherwise None.
    """
    doctors: Collection = get_doctor_collection()
    
    # Query the database for the doctor with the given email; exclude the MongoDB ID and password from the result
    doctor = doctors.find_one({"email": email.lower()}, {"_id": 0})
    return doctor

def get_current_doctor(request: Request) -> dict:
    """
    Extracts and verifies the current doctor from the JWT token.

    Args:
        request (Request): The incoming HTTP request containing the Authorization header.

    Raises:
        HTTPException: If the token is missing, invalid, expired, or the doctor does not exist.

    Returns:
        dict: The decoded JWT payload containing doctor information.
    """
    logger.info("Checking for Authorization header in request.")
    auth_header = request.headers.get("Authorization")
    logger.info(f"Auth Header: {auth_header}")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.error("Missing or invalid Authorization header. Provided header: %s", auth_header)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header"
        )

    # Extract the token without logging the actual token value for security.
    token = auth_header.split(" ")[1]
    logger.info("Authorization header found. Token extracted (not logging token for security).")

    try:
        doctor_data = verify_token(token)  # Decode and verify the JWT token
        logger.info("JWT token verified successfully. Decoded data: %s", doctor_data)

        # Validate that the doctor exists in the database.
        doctor = get_doctor_by_id(doctor_data.get("id"))
        if not doctor:
            logger.error("Doctor with id %s not found.", doctor_data.get("id"))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Doctor not found"
            )

        logger.info("Doctor with id %s successfully authenticated.", doctor_data.get("id"))
        return doctor

    except HTTPException as http_err:
        logger.error("HTTPException during token verification: %s", http_err.detail)
        raise http_err

    except Exception as e:
        logger.exception("Unexpected error during token verification: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
        