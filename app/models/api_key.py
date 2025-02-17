"""API Key Management for Doctor Access."""

from datetime import datetime
from datetime import timedelta
import logging
import secrets
import uuid

from app.config import config as env
from app.config.db_init import db_handler
from fastapi import HTTPException
from fastapi import status
from pymongo.collection import Collection

# Configure logger
logger = logging.getLogger(__name__)


def get_api_key_collection() -> Collection:
    """Retrieves the MongoDB API key collection.

    Returns:
        Collection: The MongoDB collection storing API keys.

    Raises:
        HTTPException: 500 if the database collection is unavailable.
    """
    try:
        collection = db_handler.get_collection(
            collection_name=env.get_api_keys_collection(), database="Users"
        )
        if collection is None:
            logger.error("API key collection is unavailable.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed.",
            )

        return collection

    except Exception as e:
        logger.exception(
            "Unexpected error retrieving API key collection: %s", str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )


def generate_api_key() -> str:
    """Generates a secure random API key.

    Returns:
        str: A 64-character hexadecimal API key.
    """
    return secrets.token_hex(32)  # Generates a secure 64-character API key


def get_api_key(doctor_id: str) -> str:
    """Retrieves the API key associated with a given doctor ID.

    Args:
        doctor_id (str): The unique identifier of the doctor.

    Returns:
        str: The API key assigned to the doctor.

    Raises:
        HTTPException: 400 if the doctor ID is missing.
        HTTPException: 404 if no API key is found.
        HTTPException: 500 if an internal error occurs.
    """
    if not doctor_id:
        logger.error("Doctor ID is required to retrieve the API key.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor ID is missing.",
        )

    try:
        api_keys = get_api_key_collection()
        api_key_record = api_keys.find_one(
            {"doctor_id": doctor_id}, {"_id": 0, "api_key": 1}
        )

        if not api_key_record:
            logger.warning("No API key found for doctor ID: %s", doctor_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found.",
            )

        logger.info(
            "Successfully retrieved API key for doctor ID: %s", doctor_id
        )
        return api_key_record["api_key"]

    except Exception as error:
        logger.exception(
            "Unexpected error while retrieving API key: %s", str(error)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving API key.",
        )


def allocate_api_key(doctor_id: str) -> str:
    """Allocates and stores an API key for a doctor.

    Args:
        doctor_id (str): The unique identifier of the doctor.

    Returns:
        str: The allocated API key.

    Raises:
        HTTPException: 400 if the doctor ID is missing.
        HTTPException: 500 if API key allocation fails.
    """
    if not doctor_id:
        logger.error("Doctor ID is required to allocate an API key.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor ID is missing.",
        )

    try:
        api_keys = get_api_key_collection()

        # Check if an API key already exists for the doctor
        existing_api_key = api_keys.find_one(
            {"doctor_id": doctor_id}, {"_id": 0, "api_key": 1}
        )
        if existing_api_key:
            logger.warning(
                "API key already exists for doctor ID: %s", doctor_id
            )
            return existing_api_key["api_key"]

        # Generate a new API key
        api_key = generate_api_key()
        created_at = datetime.now()
        expired_at = created_at + timedelta(days=30)

        # Prepare the API key record
        api_key_data = {
            "api_key_id": str(uuid.uuid4()),
            "doctor_id": doctor_id,
            "api_key": api_key,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "expired_date": expired_at.strftime("%Y-%m-%d %H:%M:%S"),
            "usage": 1000,
        }

        # Insert the API key record into the database
        result = api_keys.insert_one(api_key_data)
        if not result.acknowledged:
            logger.error(
                "Failed to allocate API key for doctor ID: %s", doctor_id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API key allocation failed.",
            )

        logger.info(
            "API key allocated successfully for doctor ID: %s", doctor_id
        )
        return api_key

    except Exception as e:
        logger.exception("Error allocating API key: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key allocation error.",
        )
