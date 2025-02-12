"""MongoDB connection handler for the Skin Diagnosis System API."""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class MongoDBHandler:
    """Handles MongoDB connections for the Skin Diagnosis System API.

    This class initializes and manages a persistent MongoDB connection using the 
    provided environment variables.

    Attributes:
        MONGO_USERNAME (str): The MongoDB username from environment variables.
        MONGO_PASSWORD (str): The MongoDB password from environment variables.
        DB_NAME (str): The name of the MongoDB database.
        MONGO_URI (str): The connection URI for MongoDB.
        client (MongoClient): The MongoDB client instance for persistent connection.
    """

    def __init__(self):
        """Initializes the MongoDBHandler class.

        Establishes the MongoDB connection using credentials from environment 
        variables and sets up the client for persistent usage.

        Raises:
            ConnectionFailure: If the database connection cannot be established.
        """
        self.MONGO_USERNAME = os.getenv("MONGO_USERNAME")
        self.MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
        self.DB_NAME = os.getenv("DB_NAME", "skin_diagnosis_db")
        self.MONGO_CLUSTER = os.getenv("MONGO_CLUSTER","cluster0.sst2o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        self.MONGO_URI = (
            f"mongodb+srv://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@{self.MONGO_CLUSTER}"
        )
        self.client = None  # Client will be initialized in the connect() method

    def connect(self):
        """Establishes a persistent connection to the MongoDB database.

        Raises:
            ConnectionFailure: If the database connection cannot be established.
        """
        if not self.client:
            try:
                self.client = MongoClient(
                    self.MONGO_URI,
                    serverSelectionTimeoutMS=5000
                )
                # Trigger exception if connection fails
                self.client.admin.command('ping')
                print("✅ Connected to MongoDB successfully")
            except ConnectionFailure as e:
                print(f"❌ MongoDB connection failed: {e}")
                raise ConnectionFailure("Could not connect to MongoDB")

    def disconnect(self):
        """Closes the connection to the MongoDB database."""
        if self.client:
            self.client.close()
            self.client = None
            print("🔌 Disconnected from MongoDB successfully")

    def get_database(self, database: str = None):
        """Retrieves the MongoDB database instance using the persistent connection.

        Args:
            database (str, optional): The name of the database to retrieve. 
                Defaults to the DB_NAME from environment variables.

        Returns:
            Database: The MongoDB database instance.

        Raises:
            ConnectionFailure: If not connected to MongoDB.
        """
        if not self.client:
            raise ConnectionFailure("Not connected to MongoDB. Call connect() first.")

        logging.info(f"Getting database: {database}")
        
        return self.client[database or self.DB_NAME]

    def get_collection(self, collection_name: str, database: str = None):
        """Retrieves a specific collection from the MongoDB database.

        Args:
            collection_name (str): The name of the collection to retrieve.
            database (str, optional): The name of the database. Defaults to the DB_NAME.

        Returns:
            Collection: The MongoDB collection instance.
        """
        db = self.get_database(database)
        
        logging.info(f"Getting collection: {collection_name}")
        return db[collection_name]
