"""User management routes with proper HTTP responses."""

import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.users import create_user, get_user_by_id, get_all_users
from schema.users import UserCreate, UserDB
from pymongo.collection import Collection

router = APIRouter()

@router.post("/register", response_model=UserDB, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate):
    """Registers a new user in the system.

    Args:
        user_in (UserCreate): The user data.

    Raises:
        HTTPException 400: If the email is already registered.
        HTTPException 500: If an error occurs during registration.

    Returns:
        UserDB: The created user details.
    """
    try:
        existing_user = get_user_by_id(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered."
            )

        user_data = create_user(
            email=user_in.email,
            full_name=user_in.full_name,
            role=user_in.role,
            password=user_in.password  # Hashing should be implemented
        )
        return UserDB(**user_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.get("/users", response_model=List[UserDB], status_code=status.HTTP_200_OK)
def get_users():
    """Fetches all users from the system.

    Raises:
        HTTPException 500: If database retrieval fails.

    Returns:
        List[UserDB]: A list of all registered users.
    """
    try:
        users = get_all_users()
        return users

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}"
        )

@router.get("/users/{user_id}", response_model=UserDB, status_code=status.HTTP_200_OK)
def get_user(user_id: str):
    """Retrieves a specific user by UUID.

    Args:
        user_id (str): The UUID of the user.

    Raises:
        HTTPException 400: If the UUID format is invalid.
        HTTPException 404: If the user is not found.
        HTTPException 500: If an internal error occurs.

    Returns:
        UserDB: The requested user.
    """
    try:
        # Validate UUID format
        try:
            uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found."
            )

        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        return user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}"
        )
