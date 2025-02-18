import logging
import os
import sys
from pathlib import Path
from decouple import config

# Detect if running inside Docker
IS_DOCKER = Path("/app").exists()

# Define the base directory
BASE_DIR = Path(__file__).resolve().parent.parent  # Points to project root

# Determine if running tests
IS_TESTING = "pytest" in sys.modules or any("pytest" in arg for arg in sys.argv)

# -------------------- ACCESSORS -------------------- #

# App
def get_port():
    return config("PORT", default=8000, cast=int)

# Authentication
def get_secret_key():
    return config("SECRET_KEY", default="default_secret")  # Avoid exposing secrets

def get_algorithm():
    return config("ALGORITHM", default="HS256")

def get_access_token_expiry():
    return config("ACCESS_TOKEN_EXPIRE_MINUTES", default=(10 if IS_TESTING else 60), cast=int)

# Database
def get_db_name():
    return config("DB_NAME", default=("TEST_SKIN_DIAGNOSIS_DB" if IS_TESTING else "Skin_Cancer_Diagnosis"))

def get_mongo_cluster():
    return config("MONGO_CLUSTER", default="default_cluster.mongodb.net")

def get_mongo_username():
    return config("MONGO_USERNAME", default="default_user")

def get_mongo_password():
    return config("MONGO_PASSWORD", default="default_password")

def get_cases_collection():
    return config("CASES_DB_COLLECTION", default="Cases")

def get_doctors_collection():
    return config("DOCTORS_DB_COLLECTION", default="Doctors")

def get_patients_collection():
    return config("PATIENTS_DB_COLLECTION", default="Patients")

def get_api_keys_collection():
    return config("API_DB_COLLECTION", default="Users-API-Keys")

def get_images_collection():
    return config("IMAGES_DB_COLLECTION", default="Images")

def get_ml_api_url():
    return config("ML_API_URL", default="http://localhost:8000/predict")

# Security & Cryptography
def get_bcrypt_salt_rounds():
    return config("BCRYPT_SALT_ROUNDS", default=12, cast=int)

# Flags
def is_testing():
    return IS_TESTING

def is_logging_enabled():
    return config("LOGGING_ENABLED", default=True, cast=bool)

# -------------------- LOGGING -------------------- #
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO if is_logging_enabled() else logging.WARNING)
