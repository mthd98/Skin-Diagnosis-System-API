# Project Documentation

## 1. Project Overview

### Project Description

The Skin Diagnosis API integrates an AI-powered machine learning model for skin condition analysis. The default ML-API used in this project is linked to [Skin-Diagnosis-ML-API](https://github.com/mthd98/Skin-Diagnosis-ML-API); however, the system is flexible and can be configured to use another ML API if needed.

The Skin Diagnosis API is a Python-based application designed to facilitate the diagnosis and management of skin conditions using AI-powered image analysis. It provides a robust API for handling patient cases, doctor management, and secure authentication. Built with FastAPI and MongoDB, it ensures scalability, security, and efficient data storage using GridFS for handling medical images.

This project is a Python-based application structured to support API interactions and database operations. It includes configurations for environment variables, logging, and database initialization.

## 2. Installation & Setup

### Prerequisites

- Python 3.x
- pip (Python package manager)
- MongoDB Cloud (Atlas)

### Dependencies

- The application relies on the [Skin-Diagnosis-ML-API](https://github.com/mthd98/Skin-Diagnosis-ML-API) for machine learning-based skin condition analysis. However, it can be configured to use an alternative ML API if needed.

### Installation Steps

1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd <project-folder>
   ```
2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Copy `.env` file from `.env.example` to `.env`

## 3. Configuration

The application uses environment variables for configuration. These are stored in `.env` file . Key settings include:

```ini
# .env.example
# Database Configuration
MONGO_USERNAME=Test01
MONGO_PASSWORD=DHsj8gjnEWR0QLgy
MONGO_CLUSTER=cluster0.sst2o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DB_NAME=Skin_Cancer_Diagnosis
CASES_DB_COLLECTION=Cases
DOCTORS_DB_COLLECTION=Doctors
PATIENTS_DB_COLLECTION=Patients
API_DB_COLLECTION=Users-API-Keys
IMAGES_DB_COLLECTION=Images
ML_API_URL=http://localhost:8000/predict

# JWT Configuration
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Bcrypt Salt Rounds (Optional)
BCRYPT_SALT_ROUNDS=12

# Logging
LOGGING_ENABLED=FALSE

# App
PORT=8000
```

These variables define the database connection, authentication configurations, and application settings. Ensure they are correctly configured before running the application.

The application uses environment variables for configuration. These are stored in `.env` files located in `app/config/`. Key settings include:

- `MONGO_URI`: Connection string for MongoDB Cloud (Atlas)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- Other API keys or credentials as needed

## 4. Database Structure

The database consists of the following collections:

- **API Keys** (`api_key.py`): Manages API keys linked to doctors with expiration dates and usage limits.
- **Authentication** (`authentication.py`): Stores login credentials and authentication tokens.
- **Cases** (`case.py`): Records diagnosis cases, including images, doctor assignments, and notes.
- **Doctors** (`doctor.py`): Manages doctor profiles, including credentials and API key associations.
- **Patients** (`patient.py`): Stores patient records, including personal details and medical history.
- **Images Storage (GridFS)**: Instead of a traditional collection, images are stored using MongoDB’s GridFS. This allows for efficient storage and retrieval of large medical images by breaking them into smaller chunks and storing metadata separately. For more details, refer to [MongoDB GridFS Documentation](https://www.mongodb.com/docs/manual/core/gridfs/).

## 5. API Endpoints

### Case Management Endpoints:

- **Create a new case** (POST `/new_case`): Creates a new diagnosis case.
- **Get a case by ID** (GET `/cases/{case_id}`): Fetches a specific case by ID.
- **Get all cases assigned to a doctor** (GET `/get_cases`): Retrieves all cases assigned to the authenticated doctor.
- **Get cases for a specific patient** (GET `/cases/patient/{patient_id}`): Fetches all cases associated with a specific patient.

### User Management Endpoints:

- **Register a doctor** (POST `/register-doctor`): Registers a new doctor.
- **Doctor login** (POST `/login`): Authenticates a doctor.
- **Register a patient** (POST `/register-patient`): Registers a new patient.
- **Get all doctors** (GET `/doctors`): Retrieves a list of all registered doctors.
- **Get a patient by patient number** (GET `/patients/{patient_number}`): Fetches a patient’s details using their patient number.

## 6. Usage Instructions

- The application is built using [FastAPI](https://fastapi.tiangolo.com/) for high-performance API interactions.
- It is served using [Uvicorn](https://www.uvicorn.org/), an ASGI server for running FastAPI applications.
- Run the application:
  ```sh
  python -m uvicorn app.main:app --reload
  ```
- Access the API via the configured endpoints

## 7. Docker Instructions

### Building the Docker Image

To containerize the application, build the Docker image using:

```sh
 docker build -t skin-diagnosis-api .
```

### Running the Docker Container

Run the containerized application using:

```sh
 docker run -d -p 8000:8000 --name skin-diagnosis-api-container skin-diagnosis-api
```

This will start the application and expose it on port 8000.

## 8. Running Tests

For more information on pytest, refer to the [official documentation](https://docs.pytest.org/en/latest/).

To ensure the application functions correctly, run the tests using `pytest`:

### Running All Tests

```sh
pytest tests/
```

### Running Specific Tests

To run a specific test file:

```sh
pytest tests/test_auth.py
```

To run a specific test case inside a file:

```sh
pytest tests/test_auth.py::test_login
```

### Running Tests with Coverage Report

For a test coverage report, use:

```sh
pytest --cov=app tests/
```

This will show the percentage of code covered by tests.

## 9. Project Structure

```
app/
 ├── config/
 │   ├── .env
 │   ├── config.py
 │   ├── db_init.py
 │   ├── logging_config.py
 ├── db/
 │   ├── MongoDB.py
 ├── external_services/
 │   ├── Email.py
 ├── middleware/
 │   ├── authentication.py
 ├── models/
 │   ├── api_key.py
 │   ├── case.py
 │   ├── doctor.py
 │   ├── patient.py
 ├── routers/
 │   ├── cases.py
 │   ├── users.py
 ├── schema/
 │   ├── api_key.py
 │   ├── authentication.py
 │   ├── case.py
 │   ├── doctor.py
 │   ├── images.py
 │   ├── patient.py
 ├── utils/
 │   ├── authentication.py
 ├── main.py
 ├── __init__.py
 ├── tests/
 │   ├── conftest.py
 │   ├── run_tests.py
 │   ├── test_auth.py
 │   ├── test_config.py
 │   ├── test_documentation.py
 │   ├── test_logging.py
 │   ├── test_main.py
 │   ├── test_security.py
 │   ├── test_serialization.py
 │   ├── fixtures/
 │   │   ├── db_fixtures.py
 │   │   ├── mock_data.py
 │   ├── integration/
 │   │   ├── test_database.py
 │   │   ├── test_routes.py
 │   ├── unit/
 │   │   ├── test_models.py
 │   │   ├── test_schemas.py
```

## 10. Contributing

- Fork the repository and create a new branch for changes
- Commit and push changes to your branch
- Submit a pull request for review

### Repository Links

- **GitHub Repository:** [Enter GitHub repository URL]
- **Documentation Repository:** [Enter documentation repository URL]

### Contributions

Below are the contributors to the project, along with their profiles:

* [**Thabang Maribana**](https://github.com/Saint2209)

* [**Contributor 2:**]()

* [**Contributor 3:**]()

* [**Contributor 4:**]()

* [**Contributor 5:**]()

* [**Contributor 6:**]()

- Fork the repository and create a new branch for changes
- Commit and push changes to your branch
- Submit a pull request for review

## 11. License

This project is licensed under the MIT License. See `LICENSE` for details.

