"""Doctor management module for handling authentication, profile creation, and retrieval."""

from datetime import datetime
from datetime import timezone
import logging
import uuid

from app.config import config as env
from app.config.db_init import db_handler
from app.models.api_key import allocate_api_key
from app.schema.doctor import DoctorCreate
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pymongo.collection import Collection

# Configure logger
logger = logging.getLogger(__name__)


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
            collection_name=env.get_doctors_collection(), database="Users"
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
    """Creates a new doctor in the database.

    Args:
        doctor_info (DoctorCreate): The validated doctor details.

    Returns:
        JSONResponse: A JSON response containing the created doctor profile.

    Raises:
        HTTPException: 500 if database insertion fails.
    """
    from app.utils.authentication import hash_password

    try:
        logger.info("Doctor registration input: %s", doctor_info.model_dump())

        existing_doctor = get_doctor_by_email(doctor_info.email)
        if existing_doctor:
            logger.error("Email is already registered: %s", doctor_info.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered.",
            )

        logger.info("Creating doctor profile for email: %s", doctor_info.email)

        doctors = get_doctor_collection()

        doctor_data = {
            "doctor_id": str(uuid.uuid4()),
            "email": doctor_info.email.lower(),
            "name": doctor_info.name.title(),
            "password": hash_password(doctor_info.password),
            "created_at": datetime.now(timezone.utc),
        }

        result = doctors.insert_one(doctor_data)
        if not result.acknowledged:
            logger.error(
                "Database insert for doctor %s not acknowledged.",
                doctor_info.email,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database insert failed.",
            )

        doctor_data["api_key"] = allocate_api_key(doctor_data["doctor_id"])

        # Remove sensitive fields before returning the response
        doctor_data.pop("password", None)
        doctor_data.pop("_id", None)

        logger.info(
            "Doctor created successfully with id: %s", doctor_data["doctor_id"]
        )
        return JSONResponse(
            content=jsonable_encoder(doctor_data),
            status_code=status.HTTP_201_CREATED,
        )

    except Exception as e:
        logger.exception("Error creating doctor: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating doctor.",
        )


def get_doctor_by_id(doctor_id: str) -> dict:
    """Retrieves a doctor by their UUID.

    Args:
        doctor_id (str): The UUID string of the doctor.

    Returns:
        dict: The doctor object if found, otherwise None.
    """
    return get_doctor_collection().find_one(
        {"doctor_id": doctor_id}, {"_id": 0, "password": 0}
    )


def get_all_doctors() -> JSONResponse:
    """Retrieves all doctors from the database.

    Returns:
        JSONResponse: A JSON response containing a list of doctors.

    Raises:
        HTTPException: 500 if an error occurs.
    """
    try:
        doctors = get_doctor_collection()
        doctor_list = list(doctors.find({}, {"_id": 0, "password": 0}))
        return JSONResponse(
            content={"doctors": jsonable_encoder(doctor_list)},
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving doctors: {str(e)}",
        )


def get_doctor_by_email(email: str) -> dict:
    """Retrieves a doctor by their email.

    Args:
        email (str): The doctor's email address.

    Returns:
        dict: The doctor object if found, otherwise None.
    """
    return get_doctor_collection().find_one(
        {"email": email.lower()}, {"_id": 0}
    )


def get_current_doctor(request: Request) -> dict:
    """Extracts and verifies the current doctor from the JWT token.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        dict: The decoded JWT payload containing doctor information.

    Raises:
        HTTPException: 401 if the token is missing or invalid.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.error("Missing or invalid Authorization header.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header.",
        )

    token = auth_header.split(" ")[1]
    logger.info("Authorization header found. Extracting token.")

    from app.utils.authentication import verify_token

    try:
        doctor_data = verify_token(token)
        logger.info("JWT token verified successfully.")

        doctor = get_doctor_by_id(doctor_data.get("id"))
        if not doctor:
            logger.error("Doctor with id %s not found.", doctor_data.get("id"))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Doctor not found.",
            )

        logger.info("Doctor authenticated successfully.")
        return doctor

    except HTTPException as http_err:
        logger.error("Token verification error: %s", http_err.detail)
        raise http_err

    except Exception as e:
        logger.exception(
            "Unexpected error during token verification: %s", str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )
