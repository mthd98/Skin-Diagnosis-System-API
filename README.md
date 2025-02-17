# Project Documentation

## 1. Project Overview
This project is a Python-based application structured to support API interactions and database operations. It includes configurations for environment variables, logging, and database initialization.

## 2. Installation & Setup
### Prerequisites
- Python 3.x
- pip (Python package manager)
- MongoDB Cloud (Atlas)

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
   - Copy `.env` file from `config/.env.example` to `config/.env`
   - Configure MongoDB Cloud connection settings in `config/config.py`

## 3. Configuration
The application uses environment variables for configuration. These are stored in `.env` files located in `app/config/`. Key settings include:
- `MONGO_URI`: Connection string for MongoDB Cloud (Atlas)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- Other API keys or credentials as needed

## 4. Database Structure
This project interacts with a MongoDB Cloud (Atlas) database. The database connection is initialized in `app/config/db_init.py`, and database operations are managed through `app/db/MongoDB.py`.

## 5. API Endpoints (if applicable)
If the application exposes an API, endpoints will be defined in `app/main.py` or corresponding router files in `app/routers/`.

## 6. Usage Instructions
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
 docker run -d -p 5000:5000 --name skin-diagnosis-api-container skin-diagnosis-api
```
This will start the application and expose it on port 8000.

## 8. Project Structure
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

## 9. Contributing
- Fork the repository and create a new branch for changes
- Commit and push changes to your branch
- Submit a pull request for review

## 10. License
This project is licensed under the MIT License. See `LICENSE` for details.

