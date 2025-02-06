"""User management routes with authentication and proper HTTP responses."""

import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from api.models.users import create_user, get_user_by_id, get_all_users, get_user_by_email
from api.schema.users import UserCreate, UserDB
from api.utils.authentication import hash_password, get_current_user, require_role

router = APIRouter()

# -------- User Registration --------

@router.post("/register", response_model=UserDB, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate):
    """Registers a new user with hashed password.

    Args:
        user_in (UserCreate): The user data.

    Raises:
        HTTPException 400: If the email is already registered.
        HTTPException 500: If an error occurs during registration.

    Returns:
        UserDB: The created user details.
    """
    try:
        existing_user = get_user_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered."
            )

        hashed_password = hash_password(user_in.password)
        user_data = create_user(
            email=user_in.email,
            full_name=user_in.full_name,
            role=user_in.role,
            password=hashed_password
        )
        return UserDB(**user_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

# -------- Get All Users (Protected Route) --------

@router.get("/users", response_model=List[UserDB], status_code=status.HTTP_200_OK)
def get_users(current_user: dict = Depends(get_current_user)):
    """Fetches all users (accessible to authenticated users only).

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

# -------- Get User by ID --------

@router.get("/users/{user_id}", response_model=UserDB, status_code=status.HTTP_200_OK)
def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
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
            uuid_obj = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid UUID format."
            )

        user = get_user_by_id(str(uuid_obj))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        return UserDB(**user)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}"
        )

# Protect route: Only SuperUser can access
@router.get("/admin-only")
def admin_dashboard(current_user: dict = Depends(require_role(["superuser"]))):
    return {"message": f"Welcome, SuperUser {current_user['email']}!"}

# Protect route: Only Doctors and SuperUsers can access
@router.get("/doctor-dashboard")
def doctor_dashboard(current_user: dict = Depends(require_role(["doctor", "superuser"]))):
    return {"message": f"Welcome, {current_user['role']} {current_user['email']}!"}