"""MongoDB model for skin diagnosis cases with image support."""

from datetime import datetime, timezone
import os
import logging
import uuid
from fastapi import Depends, HTTPException, UploadFile, requests, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import gridfs
from pymongo.collection import Collection
from app.schema.case import Case, DiagnosisResult
from app.schema.images import UploadImage
from app.models.doctor import get_current_doctor
from app.models.patient import get_patient_id
from app.models.api_key import get_api_key
from app.config.db_init import db_handler
from dotenv import load_dotenv
import requests 
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Use environment variables
CASES_DB_COLLECTION  = os.getenv("CASES_DB_COLLECTION")
IMAGES_DB_COLLECTION = os.getenv("IMAGES_DB_COLLECTION")
ML_API_URL = os.getenv("ML_API_URL")

def get_fs() -> gridfs.GridFS:
    """
    Initializes and returns a GridFS instance for handling large files.

    Returns:
        gridfs.GridFS: The GridFS instance connected to the Images database.

    Raises:
        HTTPException: If the database connection fails or GridFS initialization encounters an error.
    """
    try:
        # Step 1: Retrieve the database instance
        logger.info("Attempting to connect to the 'Images' database.")
        db = db_handler.get_database("Images")  
        
        if db is None:
            logger.error("Database connection failed: 'Images' database not found.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed. 'Images' database not found."
            )

        # Step 2: Initialize GridFS with the database
        logger.info("Successfully connected to 'Images' database. Initializing GridFS.")
        return gridfs.GridFS(db)

    except HTTPException as http_err:
        logger.error(f"HTTP error occurred: {http_err.detail}")
        raise http_err

    except Exception as e:
        logger.exception(f"Unexpected error during GridFS initialization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while initializing GridFS: {str(e)}"
        )

def get_case_collection() -> Collection:
    """Retrieves the MongoDB case collection.

    Returns:
        Collection: MongoDB collection for cases.
    """
    db = db_handler.get_collection(
        collection_name=CASES_DB_COLLECTION, 
        database="Cases")
    if db is None:
            error_message = "Cases collection is unavailable."
            logging.error(error_message)
            raise Exception(error_message)
    logging.info("Got cases collection: %s", db)
    return db

def get_case_by_id(case_id: str) -> JSONResponse:
    """
    Retrieve a case from the database using its unique ID and return it as a CaseDB model.

    Args:
        case_id (str): The unique identifier of the case.

    Returns:
        CaseDB: The case document wrapped in a CaseDB instance, which is JSON serializable.

    Raises:
        HTTPException: 404 if the case is not found, 500 for any internal errors.
    """
    try:
        # Retrieve the case from the database, excluding the internal '_id' field.
        case = get_case_collection().find_one({"case_id": case_id}, {"_id": 0})

        # If no case is found, raise a 404 error.
        if case is None:
            logger.warning(f"Case with ID {case_id} not found.")
            raise HTTPException(status_code=404, detail="Case not found")

        # # Ensure 'notes' exists, defaulting to an empty list if missing
        # if "notes" not in case:
        #     logger.info(f"'notes' field missing for case {case_id}. Initializing as an empty list.")
        #     case["notes"] = []

        # Create a CaseDB instance from the retrieved data.
        # Convert to JSON serializable format
        case_data = jsonable_encoder(Case(**case))

        logger.info(f"Case retrieved successfully for case_id: {case_id}")

        # Return the JSONResponse with status 200
        return JSONResponse(
            content=case_data,
            status_code=status.HTTP_200_OK
        )

    except HTTPException as http_err:
        logger.error(f"HTTP error occurred while retrieving case: {http_err.detail}")
        raise http_err

    except Exception as error:
        logger.exception(f"An unexpected error occurred while retrieving the case: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving the case: {str(error)}"
        )
   
def get_cases_by_doctor(doctor: dict) -> JSONResponse:
    """
    Retrieve all cases assigned to a specific doctor using the doctor's ID.

    Args:
        doctor_id (str): The unique identifier of the doctor.

    Returns:
        JSONResponse: A JSON response containing a list of case documents associated with the doctor.
    """
    try:
        
        doctor_id = doctor["doctor_id"]
        # Retrieve all cases for the given doctor_id, excluding the internal '_id' field
        cases_cursor = get_case_collection().find({"doctor_id": doctor_id}, {"_id": 0})
        cases_list = list(cases_cursor)

        # If no cases are found, return an empty list with 200 status
        if not cases_list:
            logger.warning(f"No cases found for doctor ID {doctor_id}.")
            return JSONResponse(
                content={"status": "success", "cases": []},
                status_code=status.HTTP_200_OK
            )

        # Process each case to ensure schema consistency
        processed_cases = []
        for case in cases_list:
            # Serialize using the Pydantic Case model
            case_data = jsonable_encoder(Case(**case))
            processed_cases.append(case_data)

        logger.info(f"Retrieved {len(processed_cases)} case(s) for doctor_id: {doctor_id}")

        # Return the processed list of cases
        return JSONResponse(
            content={"cases": processed_cases},
            status_code=status.HTTP_200_OK
        )

    except HTTPException as http_err:
        logger.error(f"HTTP error occurred while retrieving cases: {http_err.detail}")
        raise http_err

    except Exception as error:
        logger.exception(f"An unexpected error occurred while retrieving cases: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving the cases: {str(error)}"
        )

def get_cases_by_patient(patient_id: str) -> JSONResponse:
    """
    Retrieve all cases associated with a specific patient using the patient's ID.

    Args:
        patient_id (str): The unique identifier of the patient.

    Returns:
        JSONResponse: A JSON response containing a list of case documents associated with the patient.
    
    Raises:
        HTTPException: 404 if no cases are found, 500 for any internal errors.
    """
    try:
        # Retrieve all cases for the given patient_id, excluding the internal '_id' field
        cases_cursor = get_case_collection().find({"patient_id": patient_id}, {"_id": 0})
        cases_list = list(cases_cursor)

        # If no cases are found, return an empty list with 200 status
        if not cases_list:
            logger.warning(f"No cases found for patient ID {patient_id}.")
            return JSONResponse(
                content={"cases": []},
                status_code=status.HTTP_200_OK
            )

        # Process each case to ensure schema consistency
        processed_cases = []
        for case in cases_list:
            # Serialize using the Pydantic Case model
            case_data = jsonable_encoder(Case(**case))
            processed_cases.append(case_data)

        logger.info(f"Retrieved {len(processed_cases)} case(s) for patient_id: {patient_id}")

        # Return the processed list of cases
        return JSONResponse(
            content={"cases": processed_cases},
            status_code=status.HTTP_200_OK
        )

    except HTTPException as http_err:
        logger.error(f"HTTP error occurred while retrieving cases: {http_err.detail}")
        raise http_err

    except Exception as error:
        logger.exception(f"An unexpected error occurred while retrieving cases: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving the cases: {str(error)}"
        )

def generate_unique_filename(extension: str = "jpg") -> str:
    """
    Generates a unique filename using UUID and the current timestamp.

    Args:
        extension (str): The file extension (default is 'jpg').

    Returns:
        str: A unique filename in the format 'image_<timestamp>_<uuid>.<extension>'.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]  # Short UUID for readability
    return f"image_{timestamp}_{unique_id}.{extension}"


async def get_diagnosis(file,api_key) -> DiagnosisResult:
    """
    Sends the uploaded image file to the ML API for diagnosis.

    Args:
        file (UploadFile): The uploaded image file.

    Returns:
        DiagnosisResult: The diagnosis result containing probabilities for Malignant and Benign.
                       For now, always returns 0.0 for both.
    """
    try:
        # Read the image bytes from the uploaded file.
        file_bytes =  file
        print("#"*100)
        print(file_bytes)
        # Generate a unique filename based on the original filename.
        logger.info("Starting diagnosis process for image: %s", "image")

        # Access Token for ML API
        headers = {"access_token": str(api_key)}

        # Prepare the file payload for the API request.
        files = {"file":file_bytes}
        logger.debug("Prepared image file for API request: %s", "image")


        # Send the POST request to the ML API.
        response = requests.post(ML_API_URL, files=files, timeout=5,headers=headers)
        print("#"*100)
        print(response.json())
        logger.info("Received response from ML API with status code: %s", response.status_code)

        # Check for API errors: if status code is not 200, for now return default diagnosis.
        if response.status_code != 200:
            logger.warning("ML API returned non-200 status code: %s", response.status_code)
            # TODO: Uncomment the HTTPException below when ML API is ready to handle errors explicitly.
            raise HTTPException(
                 status_code=response.status_code,
                 detail=f"ML API error: {response.text}"
             )

        # Parse the JSON response from the ML API.
        data = response.json()
        logger.info("Response JSON from ML API: %s", data)

        # Return the diagnosis result by unpacking the diagnosis_data dictionary.
        return data

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logger.exception("Unexpected error during diagnosis: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

async def create_case(
    patient_number: int,
    file: UploadFile,
    current_doctor: dict
) -> JSONResponse:
    """
    Create a new diagnosis case by processing an uploaded image.
    
    This function performs the following:
      1. Validates that the file has an allowed image extension.
      2. Reads the file bytes asynchronously.
      3. Generates a unique filename (using the file’s extension).
      4. Creates an UploadImage instance.
      5. Validates the current doctor's credentials and retrieves the patient ID.
      6. Uploads the image to GridFS.
      7. Obtains a diagnosis result from the ML API.
      8. Inserts the new case data into the MongoDB cases collection.
    
    Args:
        patient_number (int): The unique patient number.
        file (UploadFile): The uploaded image file.
        current_doctor (dict): Details of the authenticated doctor.
    
    Returns:
        JSONResponse: A response containing the new case details.
    
    Raises:
        HTTPException: For any validation errors or unexpected issues during the process.
    """
    try:
        logger.info("Received request to create new case for patient_number: %s", patient_number)
        
        # Validate that the uploaded file is an allowed image type.
        allowed_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
        if not file.filename.lower().endswith(allowed_extensions):
            logger.error("Invalid file type for file: %s. Only image files are allowed.", file.filename)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only image files are allowed."
            )
        
        # Read the file bytes asynchronously.
        image_bytes = await file.read()
        
        logger.info("File read successfully: %s, size: %d bytes", file.filename, len(image_bytes))
        
        # Generate a unique filename while preserving the original extension.
        unique_filename = generate_unique_filename(file.filename)
        logger.info("Generated unique filename: %s", unique_filename)
        
        # Create an UploadImage instance containing the file data.
        image_data = UploadImage(image_bytes=image_bytes, image_name=unique_filename)
        
        # Validate current doctor credentials.
        doctor_id = current_doctor.get("doctor_id")
        doctor_api_key = get_api_key(doctor_id)
        print("#"*100)
        print(doctor_api_key)
        if not doctor_id:
            logger.error("Doctor ID missing in provided current_doctor data.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid doctor credentials"
            )
        
        # Retrieve the patient ID from the patient number.
        patient_id = get_patient_id(patient_number)
        if not patient_id:
            logger.error("Patient with number %s not found.", patient_number)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Upload the image to GridFS.
        image_id = upload_case_image(image_data)
        logger.info("Image uploaded successfully to GridFS with ID: %s", image_id)
        
        # Obtain the diagnosis result from the ML API.
        diagnosis_result = await get_diagnosis(image_bytes,doctor_api_key)
        diagnosis = jsonable_encoder(diagnosis_result)
        logger.info("Diagnosis obtained: %s", diagnosis)
        
        # Construct the case data payload.
        case_data = {
            "case_id": str(uuid.uuid4()),
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "diagnosis": diagnosis,
            "notes": "",
            "image_id": image_id,
            "created_at": datetime.now(timezone.utc)
        }
        
        # Insert the new case into the MongoDB collection.
        cases = get_case_collection()
        result = cases.insert_one(case_data)
        
        if not result.acknowledged:
            logger.error("Database insert for case not acknowledged.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database insert for case not acknowledged"
            )
        logger.info("Case created successfully with id: %s", case_data["case_id"])
        
        case_data.pop("_id", None)
        
        # Return the successful JSON response with the new case details.
        return JSONResponse(
            content={"status": "success", "case": jsonable_encoder(case_data)},
            status_code=status.HTTP_201_CREATED
        )
    
    except HTTPException as http_exc:
        logger.error("HTTPException during case creation: %s", http_exc.detail)
        raise http_exc
    
    except Exception as e:
        logger.exception("Unexpected error during case creation: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the case: {str(e)}"
        )
def upload_case_image(image_data: UploadImage) -> str:
    try:
        logger.info("Starting image upload process")

        file_data = image_data.image_bytes
        filename = image_data.image_name

        if not file_data or not filename:
            logger.warning("Invalid input: file_data or filename is missing")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid input: file_data or filename is missing")

        fs = get_fs()
        image_id = fs.put(file_data, filename=filename)

        logger.info(f"Image uploaded successfully with ID: {image_id}")
        return str(image_id)

    except Exception as e:
        logger.error(f"An error occurred while uploading the image: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while uploading the image: {str(e)}")

def get_case_image(image_id: str) -> bytes:
    """Retrieves an image from GridFS.

    Args:
        image_id (str): The GridFS ID of the image.

    Returns:
        bytes: The image file data.
    """
    try:
        logger.info(f"Retrieving image with ID: {image_id}")
        fs = get_fs()
        image = fs.get(image_id)
        logger.info(f"Image retrieved successfully with ID: {image_id}")
        return image.read()
    except Exception as e:
        logger.error(f"An error occurred while retrieving the image: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while retrieving the image: {str(e)}")
