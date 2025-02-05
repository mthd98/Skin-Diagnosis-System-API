"""User model for MongoDB."""

import uuid
from pymongo.collection import Collection
from api.db.MongoDB import get_database

# TODO: Get change to DB name

def get_user_collection() -> Collection:
    """Retrieves the MongoDB user collection.

    Returns:
        Collection: MongoDB collection for users.
    """
    db = get_database()
    return db["users"]

def create_user(email: str, full_name: str, role: str, password: str) -> dict:
    """Creates a new user in the database.

    Args:
        email (str): The user's email.
        full_name (str): The user's full name.
        role (str): The user's role (doctor, patient, superuser).
        password (str): The hashed password.

    Returns:
        dict: The created user object.
    """
    users = get_user_collection()
    
    user_data = {
        "id": str(uuid.uuid4()),  # Store as UUID string
        "email": email,
        "full_name": full_name,
        "role": role,
        "password": password,  # Should be hashed
    }
    
    users.insert_one(user_data)
    return user_data

def get_user_by_id(user_id: str) -> dict:
    """Retrieves a user by their UUID.

    Args:
        user_id (str): The UUID string of the user.

    Returns:
        dict: The user object, if found.
    """
    users = get_user_collection()
    return users.find_one({"id": user_id}, {"_id": 0, "password": 0})

def get_all_users() -> list:
    """Fetches all users from the database.

    Returns:
        list: A list of all users.
    """
    users = get_user_collection()
    return list(users.find({}, {"_id": 0, "password": 0}))
