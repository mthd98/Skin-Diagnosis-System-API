from datetime import datetime
from datetime import timedelta
from datetime import timezone
import logging

from app.config import config
from app.models import doctor  # Import the entire module to avoid circular dependency
from app.schema.authentication import LoginRequest
import bcrypt
from fastapi import HTTPException
from fastapi import status
import jwt

# from dotenv import load_dotenv


# ✅ Logging setup
logger = logging.getLogger(__name__)

# ----------------- Password Utilities ----------------- #


def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    try:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")
    except Exception as e:
        logger.error("Error in hash_password: %s", str(e))
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies if the provided password matches the hashed password."""
    if not hashed_password:
        logger.error(
            "verify_password: Provided hashed_password is None or empty."
        )
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception as e:
        logger.error("Error in verify_password: %s", str(e))
        return False


# ----------------- JWT Token Handling ----------------- #


def create_access_token(data: dict) -> str:
    """Generates a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=config.get_access_token_expiry()
    )
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode, config.get_secret_key(), algorithm=config.get_algorithm()
    )


def verify_token(token: str) -> dict:
    """Verifies a JWT token and returns the decoded payload."""
    try:
        payload = jwt.decode(
            token, config.get_secret_key(), algorithms=[config.get_algorithm()]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


# ----------------- User Authentication ----------------- #


def authenticate_doctor(login_data: LoginRequest) -> dict:
    """Authenticates a doctor using email and password.

    Args:
        login_data (LoginRequest): The login credentials containing email and password.

    Returns:
        dict: Contains the generated access token upon successful authentication.

    Raises:
        HTTPException: If authentication fails due to missing fields, invalid credentials,
                      or an unexpected error occurs.
    """
    try:
        if not login_data.email or not login_data.password:
            logger.error(
                "Login data is missing required fields: email or password. Received: %s",
                login_data.model_dump(),
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required.",
            )

        logger.info(
            "Attempting to authenticate doctor with email: %s", login_data.email
        )
        doctor_data = doctor.get_doctor_by_email(login_data.email.lower())
        if not doctor_data:
            logger.warning(
                "Authentication failed: No doctor found with email: %s",
                login_data.email,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        if not verify_password(
            login_data.password, doctor_data.get("password")
        ):
            logger.warning(
                "Authentication failed: Invalid password for email: %s",
                login_data.email,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password.",
            )

        access_token = create_access_token(
            data={"id": doctor_data["doctor_id"], "email": doctor_data["email"]}
        )
        logger.info(
            "JWT access token generated successfully for email: %s",
            login_data.email,
        )
        return {"access_token": access_token}

    except HTTPException as http_err:
        logger.error(
            "HTTPException during authentication for email %s: %s",
            login_data.email,
            http_err.detail,
        )
        raise http_err
    except Exception as e:
        logger.error(
            "Unexpected error during authentication for email %s: %s",
            login_data.email,
            str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during authentication: {str(e)}",
        )
