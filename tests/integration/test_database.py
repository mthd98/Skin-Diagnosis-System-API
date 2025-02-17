from app.config import config
from app.db.MongoDB import MongoDBHandler
from pymongo.errors import ConnectionFailure
import pytest


@pytest.fixture(scope="module")
def mongo_test_client():
    """Fixture to provide a test MongoDB client."""
    mongo_handler = MongoDBHandler()
    mongo_handler.connect()
    yield mongo_handler.client
    mongo_handler.disconnect()


@pytest.fixture(scope="module")
def test_database(mongo_test_client):
    """Fixture to create and clean up a test database."""
    test_db_name = config.get_db_name()
    test_db = mongo_test_client[test_db_name]
    yield test_db
    # Instead of dropping the database, drop all collections.
    for collection_name in test_db.list_collection_names():
        test_db.drop_collection(collection_name)


@pytest.mark.order(1)
def test_database_connection():
    """Test if the database connection is successfully established."""
    db_handler = MongoDBHandler()
    try:
        db_handler.connect()
        db = db_handler.get_database()
        assert db is not None
        print("Database connection successful.")
    except ConnectionFailure:
        pytest.fail("Database connection failed.")
    finally:
        db_handler.disconnect()


@pytest.mark.order(2)
def test_get_doctors_collection(test_database):
    """Test if the 'doctors' collection can be retrieved from the database."""
    collection = test_database[config.get_doctors_collection()]
    assert collection.name == config.get_doctors_collection()
    print(f"Successfully accessed doctors collection: {collection.name}")


@pytest.mark.order(3)
def test_insert_and_retrieve_doctor(test_database):
    """Test inserting and retrieving a doctor from the database."""
    doctors_collection = test_database[config.get_doctors_collection()]
    sample_doctor = {
        "name": "Dr. Test",
        "email": "testdoctor@example.com",
        "password": "hashedpassword",
    }
    insert_result = doctors_collection.insert_one(sample_doctor)
    assert insert_result.inserted_id is not None

    retrieved_doctor = doctors_collection.find_one(
        {"email": "testdoctor@example.com"}
    )
    assert retrieved_doctor is not None
    assert retrieved_doctor["name"] == "Dr. Test"

    print("Doctor inserted and retrieved successfully.")


@pytest.mark.order(4)
def test_cleanup_database(test_database):
    """Test removing all test data from the database."""
    # Drop the doctors collection specifically.
    test_database.drop_collection(config.get_doctors_collection())
    remaining_collections = test_database.list_collection_names()
    assert config.get_doctors_collection() not in remaining_collections
    print("Doctors collection successfully removed from test database.")
