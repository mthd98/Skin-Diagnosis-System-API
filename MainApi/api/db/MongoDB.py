"""MongoDB connection handler for the Skin Diagnosis System API."""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Environment variables for MongoDB connection
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "skin_diagnosis_db")

# Construct MongoDB URI
MONGO_URI = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@cluster0.sst2o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# ---------------- MongoDB Client Setup ---------------- #

def get_database():
    """Establishes a connection to the MongoDB database.

    Raises:
        ConnectionFailure: If the database connection cannot be established.

    Returns:
        Database: The MongoDB database instance.
    """
    try:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000
        )
        # Trigger exception if connection fails
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        return client[DB_NAME]

    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise ConnectionFailure("Could not connect to MongoDB")

get_database()