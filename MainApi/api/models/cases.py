"""MongoDB model for skin diagnosis cases with image support."""

import uuid
import gridfs
from pymongo.collection import Collection
from api.db.MongoDB import get_database

# Initialize GridFS for handling large files
db = get_database()
fs = gridfs.GridFS(db)

def get_case_collection() -> Collection:
    """Retrieves the MongoDB case collection.

    Returns:
        Collection: MongoDB collection for cases.
    """
    return db["cases"]

def create_case(doctor_id: str, patient_id: str, diagnosis: str, notes: str, image_id: str = None) -> dict:
    """Creates a new case in the database.

    Args:
        doctor_id (str): The UUID of the doctor handling the case.
        patient_id (str): The UUID of the patient.
        diagnosis (str): The diagnosis result.
        notes (str): Additional notes.
        image_id (str, optional): The GridFS ID of the uploaded image.

    Returns:
        dict: The created case object.
    """
    cases = get_case_collection()
    
    case_data = {
        "id": str(uuid.uuid4()),  # Assign a UUID string
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "diagnosis": diagnosis,
        "notes": notes,
        "image_id": image_id  # Stores reference to GridFS image
    }
    
    cases.insert_one(case_data)
    return case_data

def upload_case_image(file_data: bytes, filename: str) -> str:
    """Uploads an image to GridFS and returns its ID.

    Args:
        file_data (bytes): The image file data.
        filename (str): The name of the file.

    Returns:
        str: The GridFS ID of the stored image.
    """
    image_id = fs.put(file_data, filename=filename)
    return str(image_id)

def get_case_image(image_id: str) -> bytes:
    """Retrieves an image from GridFS.

    Args:
        image_id (str): The GridFS ID of the image.

    Returns:
        bytes: The image file data.
    """
    image = fs.get(image_id)
    return image.read()
