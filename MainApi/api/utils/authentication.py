"""Authentication utilities for the Skin Diagnosis API."""

import jwt
import bcrypt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, Request, status

# Secret key for JWT signing (should be stored securely in production)
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token expiration time

# ---------------- Password Hashing ---------------- #

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt.

    Args:
        password (str): The plain password.

    Returns:
        str: The hashed password.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies if the provided password matches the hashed password.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password from the database.

    Returns:
        bool: True if passwords match, else False.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# ---------------- JWT Token Handling ---------------- #

def create_access_token(data: dict) -> str:
    """Generates a JWT access token.

    Args:
        data (dict): The payload data (e.g., user ID, role).

    Returns:
        str: The JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """Verifies a JWT token and returns the decoded payload.

    Args:
        token (str): The JWT token.

    Raises:
        HTTPException: If the token is invalid or expired.

    Returns:
        dict: The decoded token payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# ---------------- User Authentication ---------------- #

def get_current_user(request: Request) -> dict:
    """Extracts and verifies the current user from the JWT token.

    Args:
        request (Request): The incoming HTTP request containing the Authorization header.

    Raises:
        HTTPException: If the token is missing, invalid, or expired.

    Returns:
        dict: The decoded JWT payload containing user information.
    """
    # Check for the Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    # Extract the token
    token = auth_header.split(" ")[1]
    try:
        user_data = verify_token(token)  # Decode and verify the JWT token
        return user_data
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# ---------------- Role-Based Access Control ---------------- #

def require_role(required_roles: list):
    """Decorator to restrict routes to specific roles.

    Args:
        required_roles (list): A list of roles allowed to access the route.

    Raises:
        HTTPException: If the user's role is not authorized.
    """
    def role_checker(user: dict = Depends(get_current_user)):
        if user['role'] not in required_roles:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return user

    return role_checker
