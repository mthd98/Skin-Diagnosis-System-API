import pytest
from app.config.db_init import db_handler
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_db():
    # Connect to MongoDB before tests
    db_handler.connect()
    yield
    # Disconnect after tests
    db_handler.disconnect()

@pytest.fixture
def client():
    return TestClient(app)
