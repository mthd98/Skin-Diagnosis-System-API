import logging

from app.config import config  # Import config module for environment variables
from app.db.MongoDB import MongoDBHandler
from app.main import app
from fastapi.testclient import TestClient
from pymongo import MongoClient
import pytest

# ------------------- FORCE LOAD `.env.test` ------------------- #
IS_TESTING = config.is_testing()

logger = logging.getLogger(__name__)

# ------------------- CONSTRUCT MONGO_URI ------------------- #
# Note: Your MongoDBHandler constructs its own URI without the database name.
# For tests using a direct MongoClient, we include only the cluster part.
MONGO_URI = (
    f"mongodb+srv://{config.get_mongo_username()}:"
    f"{config.get_mongo_password()}@"
    f"{config.get_mongo_cluster()}?retryWrites=true&w=majority"
)

# ------------------- FIXTURES ------------------- #


@pytest.fixture(scope="session")
def mongo_test_client():
    """Provides a direct MongoDB client instance and ensures connection."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        logger.info("Direct MongoDB connection successful.")
    except Exception as e:
        logger.error("Direct MongoDB connection failed: %s", e)
    yield client
    client.close()


@pytest.fixture(scope="session", autouse=True)
def setup_mongo():
    """Ensures the global MongoDBHandler connects before tests and disconnects after."""
    from app.config.db_init import db_handler  # Global instance used by your app

    db_handler.connect()
    yield
    db_handler.disconnect()


@pytest.fixture(scope="session")
def test_database(mongo_test_client):
    """Provides access to the test database and cleans up after tests."""
    test_db_name = config.get_db_name()
    test_db = mongo_test_client[test_db_name]
    yield test_db
    mongo_test_client.drop_database(test_db_name)


@pytest.fixture(scope="session")
def test_client():
    """Provides a FastAPI TestClient with lifespan events."""
    # Using a context manager triggers the startup and shutdown events
    with TestClient(app) as client:
        yield client
