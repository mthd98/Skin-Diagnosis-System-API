import logging

from app.config import config
from app.middleware.authentication import AuthMiddleware
from app.utils.authentication import create_access_token
from app.utils.authentication import hash_password
from app.utils.authentication import verify_password
from app.utils.authentication import verify_token
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

logger = logging.getLogger(__name__)

# Create a simple FastAPI app for middleware testing
app = FastAPI()
app.add_middleware(AuthMiddleware)
client = TestClient(app)


@pytest.mark.order(1)
def test_hash_password():
    """Test password hashing function."""
    password = "securepassword"
    hashed = hash_password(password)
    assert isinstance(hashed, str)
    assert hashed != password  # Ensure it is hashed


@pytest.mark.order(2)
def test_verify_password():
    """Test password verification function."""
    password = "securepassword"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


@pytest.mark.order(3)
def test_create_access_token():
    """Test JWT access token creation."""
    payload = {"id": "12345", "email": "test@example.com"}
    token = create_access_token(payload)
    assert isinstance(token, str)


@pytest.mark.order(4)
def test_verify_token():
    """Test JWT token verification."""
    payload = {"id": "12345", "email": "test@example.com"}
    token = create_access_token(payload)
    decoded_payload = verify_token(token)
    assert decoded_payload["id"] == "12345"
    assert decoded_payload["email"] == "test@example.com"


@pytest.mark.order(5)
def test_public_routes():
    """Test public routes do not require authentication."""
    public_routes = [
        "/users/register-doctor",
        "/users/login",
        "/docs",
        "/openapi.json",
        "/redoc",
    ]
    for route in public_routes:
        response = client.get(route)
        assert response.status_code in [200, 404]  # Allow 404 for missing docs


@pytest.mark.order(6)
def test_missing_auth_header():
    """Test requests without an Authorization header are denied."""
    response = client.get("/protected-route")
    assert response.status_code == 401
    assert (
        response.json()["detail"] == "Missing or invalid Authorization header"
    )


@pytest.mark.order(7)
def test_invalid_token():
    """Test requests with an invalid token are denied."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/protected-route", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.order(8)
def test_valid_token():
    """Test requests with a valid token are allowed."""
    token = create_access_token({"id": "12345", "email": "test@example.com"})
    logger.info(f"Created token: {token}")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/protected-route", headers=headers)
    logger.info(f"response: {response}")
    assert response.status_code in [200, 404]
