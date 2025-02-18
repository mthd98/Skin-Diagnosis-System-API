"""MongoDB connection handler for the Skin Diagnosis System API."""

import logging
from typing import Optional

from app.config import config as env
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)


class MongoDBHandler:
    """Handles MongoDB connections dynamically using the DB_NAME from .env."""

    def __init__(self) -> None:
        """Initializes MongoDB connection parameters from environment variables."""
        self.MONGO_USERNAME: str = env.get_mongo_username()
        self.MONGO_PASSWORD: str = env.get_mongo_password()
        self.MONGO_CLUSTER: str = env.get_mongo_cluster()
        self.DB_NAME: str = env.get_db_name()

        # Ensure required credentials are set
        if not all(
            [
                self.MONGO_USERNAME,
                self.MONGO_PASSWORD,
                self.MONGO_CLUSTER,
                self.DB_NAME,
            ]
        ):
            raise ValueError(
                "Missing MongoDB credentials or database name! Check your .env file."
            )

        self.MONGO_URI = f"mongodb+srv://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@{self.MONGO_CLUSTER}"
        self.client: Optional[MongoClient] = None

    def connect(self):
        """Establishes a persistent connection to the MongoDB database.

        Raises:
            ConnectionFailure: If the database connection cannot be established.
        """
        if not self.client:
            try:
                self.client = MongoClient(
                    self.MONGO_URI, serverSelectionTimeoutMS=5000
                )
                # Trigger exception if connection fails
                self.client.admin.command("ping")
                print("Connected to MongoDB successfully: %s", self.DB_NAME)
            except ConnectionFailure as e:
                print(f"MongoDB connection failed: {e}")
                raise ConnectionFailure("Could not connect to MongoDB")

    def disconnect(self):
        """Closes the connection to the MongoDB database."""
        if self.client:
            self.client.close()
            self.client = None
            print("Disconnected from MongoDB successfully")

    def get_database(self, database: str = None) -> Database:
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
            raise ConnectionFailure(
                "Not connected to MongoDB. Call connect() first."
            )

        logging.info(f"Getting database: {database}")

        db = self.client[database or self.DB_NAME]
        return db

    def get_collection(
        self, collection_name: str, database: str = None
    ) -> Collection:
        """Retrieves a specific collection from the MongoDB database.

        Args:
            collection_name (str): The name of the collection to retrieve.
            database (str, optional): The name of the database. Defaults to the DB_NAME.

        Returns:
            Collection: The MongoDB collection instance.
        """
        db = self.get_database(database)

        logging.info(f"Getting collection: {collection_name}")
        collection = db[collection_name]
        return collection
