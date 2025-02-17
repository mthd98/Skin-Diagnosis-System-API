from datetime import datetime
from datetime import timedelta
from datetime import timezone
import logging
from unittest.mock import patch

from app.config import config
from app.schema.authentication import LoginRequest
from app.utils.authentication import authenticate_doctor
from app.utils.authentication import create_access_token
from app.utils.authentication import hash_password
from app.utils.authentication import verify_password
from app.utils.authentication import verify_token
import bcrypt
from fastapi import HTTPException
import jwt
import pytest

logger = logging.getLogger(__name__)

# Load environment variables
SECRET_KEY = config.get_secret_key()
ALGORITHM = config.get_algorithm()
ACCESS_TOKEN_EXPIRE_MINUTES = int(config.get_access_token_expiry())


# ------------------- Password Hashing Tests ------------------- #


@pytest.mark.order(1)
def test_hash_password():
    """Test that a password is correctly hashed and is not equal to the original password."""
    password = "securepassword"
    hashed_password = hash_password(password)

    assert isinstance(hashed_password, str)
    assert (
        hashed_password != password
    )  # Hash should not match the original password
    assert bcrypt.checkpw(password.encode(), hashed_password.encode())


@pytest.mark.order(2)
def test_verify_password():
    """Test password verification against a correct and incorrect password."""
    password = "securepassword"
    hashed_password = hash_password(password)

    assert verify_password(
        password, hashed_password
    )  # Correct password should return True
    assert not verify_password(
        "wrongpassword", hashed_password
    )  # Incorrect password should return False


# ------------------- JWT Token Handling Tests ------------------- #


@pytest.mark.order(3)
def test_create_access_token():
    """Test if an access token is created correctly with expiration."""
    data = {"user_id": "12345", "email": "test@example.com"}

    # Generate token
    token = create_access_token(data)

    assert isinstance(token, str)

    # DEBUG: Print Secret Key for verification
    logger.info(f"DEBUG: SECRET_KEY used for encoding - {SECRET_KEY}")

    # Ensure the SECRET_KEY is correctly loaded and used for decoding
    decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded_data["user_id"] == "12345"
    assert decoded_data["email"] == "test@example.com"
    assert "exp" in decoded_data  # Ensure expiration is set


@pytest.mark.order(4)
def test_verify_token():
    """Test verification of a valid token and invalid tokens."""
    data = {"user_id": "12345", "email": "test@example.com"}
    token = create_access_token(data)

    # Verify valid token
    decoded_data = verify_token(token)
    assert decoded_data["user_id"] == "12345"
    assert decoded_data["email"] == "test@example.com"

    # Test invalid token
    with pytest.raises(HTTPException) as excinfo:
        verify_token("invalid.token.value")
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid token"

    # Test expired token
    expired_token = jwt.encode(
        {**data, "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    try:
        verify_token(expired_token)
    except HTTPException as excinfo:
        assert excinfo.status_code == 401
        assert excinfo.detail == "Token has expired"


# ------------------- User Authentication Tests ------------------- #


@pytest.mark.order(5)
@patch("app.models.doctor.get_doctor_by_email")
def test_authenticate_doctor_success(mock_get_doctor_by_email):
    """Test successful authentication of a doctor."""
    mock_doctor_data = {
        "doctor_id": "123",
        "email": "test@example.com",
        "password": hash_password("securepassword"),
    }
    mock_get_doctor_by_email.return_value = mock_doctor_data

    login_data = LoginRequest(
        email="test@example.com", password="securepassword"
    )
    response = authenticate_doctor(login_data)
    logger.info(response)
    assert "access_token" in response
    assert isinstance(response["access_token"], str)


@pytest.mark.order(6)
@patch("app.models.doctor.get_doctor_by_email")
def test_authenticate_doctor_invalid_password(mock_get_doctor_by_email):
    """Test authentication failure due to incorrect password."""
    mock_doctor_data = {
        "doctor_id": "123",
        "email": "test@example.com",
        "password": hash_password("securepassword"),
    }
    mock_get_doctor_by_email.return_value = mock_doctor_data

    login_data = LoginRequest(
        email="test@example.com", password="wrongpassword"
    )

    with pytest.raises(HTTPException) as excinfo:
        authenticate_doctor(login_data)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid password."


@pytest.mark.order(7)
@patch("app.models.doctor.get_doctor_by_email")
def test_authenticate_doctor_invalid_email(mock_get_doctor_by_email):
    """Test authentication failure due to non-existent email."""
    mock_get_doctor_by_email.return_value = None  # Doctor not found

    login_data = LoginRequest(
        email="notfound@example.com", password="securepassword"
    )

    with pytest.raises(HTTPException) as excinfo:
        authenticate_doctor(login_data)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid email or password."


@pytest.mark.order(8)
@patch(
    "app.models.doctor.get_doctor_by_email",
    side_effect=Exception("Database connection error"),
)
def test_authenticate_doctor_exception(mock_get_doctor_by_email):
    """Test handling of unexpected errors during authentication."""
    login_data = LoginRequest(
        email="test@example.com", password="securepassword"
    )

    with pytest.raises(HTTPException) as excinfo:
        authenticate_doctor(login_data)

    assert excinfo.value.status_code == 500
    assert "Error during authentication" in excinfo.value.detail
