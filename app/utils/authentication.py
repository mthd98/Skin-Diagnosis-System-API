import bcrypt
import logging
import jwt
import os
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from dotenv import load_dotenv
from app.models import doctor  # Import the entire module to avoid circular dependency
from app.schema.authentication import LoginRequest

# Load environment variables from .env file
load_dotenv()

# Use environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Check that necessary environment variables are set
if not SECRET_KEY or not ALGORITHM:
    raise EnvironmentError("Missing SECRET_KEY or ALGORITHM in environment variables.")

# Set up logging for the module
logger = logging.getLogger(__name__)

# ---------------- Password Utilities ---------------- #

def hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt.

    Args:
        password (str): The plain text password.

    Returns:
        str: The hashed password.
    """
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error("Error in hash_password: %s", str(e))
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if the provided password matches the hashed password.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password from the database.

    Returns:
        bool: True if passwords match, else False.
    """
    if not hashed_password:
        logger.error("verify_password: Provided hashed_password is None or empty.")
        return False
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error("Error in verify_password: %s", str(e))
        return False

# ---------------- JWT Token Handling ---------------- #

def create_access_token(data: dict) -> str:
    """Generates a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    logger.debug("Creating access token for user %s with expiry at %s", data.get("email", "unknown"), expire)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """
    Verifies a JWT token and returns the decoded payload.

    Args:
        token (str): The JWT token.

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
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# ---------------- User Authentication ---------------- #

def authenticate_doctor(login_data: LoginRequest) -> dict:
    """
    Authenticates a doctor using email and password.

    Args:
        login_data (LoginRequest): The login credentials containing email and password.

    Returns:
        dict: Contains the generated access token upon successful authentication.
    """
    try:
        if not login_data.email or not login_data.password:
            logger.error("Login data is missing required fields: email or password. Received: %s", login_data.dict())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required."
            )

        logger.info("Attempting to authenticate doctor with email: %s", login_data.email)
        doctor_data = doctor.get_doctor_by_email(login_data.email.lower())
        if not doctor_data:
            logger.warning("Authentication failed: No doctor found with email: %s", login_data.email)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

        if not verify_password(login_data.password, doctor_data.get("password")):
            logger.warning("Authentication failed: Invalid password for email: %s", login_data.email)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password.")

        access_token = create_access_token(data={"id": doctor_data["doctor_id"], "email": doctor_data["email"]})
        logger.info("JWT access token generated successfully for email: %s", login_data.email)
        return {"access_token": access_token}

    except HTTPException as http_err:
        logger.error("HTTPException during authentication for email %s: %s", login_data.email, http_err.detail)
        raise http_err
    except Exception as e:
        logger.error("Unexpected error during authentication for email %s: %s", login_data.email, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during authentication: {str(e)}"
        )
