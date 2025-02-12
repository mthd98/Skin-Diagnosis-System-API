import uuid
import secrets
import logging
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from pymongo.collection import Collection
from fastapi import HTTPException, status
from app.config.db_init import db_handler

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Use environment variables
API_DB_COLLECTION = os.getenv("API_DB_COLLECTION")

def get_api_key_collection() -> Collection:
    """
    Retrieves the MongoDB API key collection.

    Returns:
        Collection: MongoDB collection for user API keys.
    """
    db = db_handler.get_collection(
        collection_name=API_DB_COLLECTION,
        database="Users"
    )
    return db

def generate_api_key() -> str:
    """Generates a secure random API key."""
    # TODO: Replace mock app with Mo's implementation
    return secrets.token_hex(32)  # 64-character hexadecimal API key

def get_api_key(doctor_id: str) -> str:
    """
    Retrieves the API key for a specific doctor using their doctor_id.

    Args:
        doctor_id (str): The unique identifier of the doctor.

    Returns:
        str: The API key associated with the doctor.

    Raises:
        HTTPException: 404 if the doctor is not found, 500 for any internal errors.
    """
    try:
        if not doctor_id:
            logger.error("Doctor ID is required to retrieve the API key.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor ID is missing."
            )

        # Allocate or retrieve the API key for the doctor
        api_keys = get_api_key_collection()
        
        api_key = api_keys.find_one({"doctor_id": doctor_id},{"_id": 0})

        logger.info(f"Successfully retrieved API key for doctor_id: {doctor_id}")
        logger.info(f"Api info:{api_key}")
        return api_key

    except HTTPException as http_err:
        logger.error(f"HTTP error occurred while retrieving API key: {http_err.detail}")
        raise http_err

    except Exception as error:
        logger.exception(f"An unexpected error occurred while retrieving API key: {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving API key: {str(error)}"
        )


def allocate_api_key(doctor_id: str) -> str:
    """
    Allocates an API key to the doctor with the given doctor_id and stores it in the API key collection.

    Args:
        doctor_id (str): The unique identifier of the doctor.

    Returns:
        str: The allocated API key.

    Raises:
        HTTPException: If the doctor does not exist or API key allocation fails.
    """
    try:
        api_keys = get_api_key_collection()

        
        # Generate the API key
        api_key = generate_api_key()

        # Check if an API key already exists for the doctor
        existing_api_key = api_keys.find_one({"doctor_id": doctor_id})
        if existing_api_key:
            logger.warning("API key already exists for doctor ID: %s", doctor_id)
            return existing_api_key["api_key"]

        # Prepare the API key data
        api_key_data = {
            "api_key_id": str(uuid.uuid4()),
            "doctor_id": doctor_id,
            "api_key": api_key,
            "created_at": datetime.now(timezone.utc),
            "usage": 0  # Track API key usage
        }

        # Insert the API key record into the API key collection
        result = api_keys.insert_one(api_key_data)
        if not result.acknowledged:
            logger.error("Failed to allocate API key for doctor ID: %s", doctor_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to allocate API key for doctor ID {doctor_id}."
            )

        logger.info("API key allocated successfully for doctor ID: %s", doctor_id)
        return api_key

    except Exception as e:
        logger.exception("Error allocating API key: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while allocating the API key: {str(e)}"
        )

