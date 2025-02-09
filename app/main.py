from fastapi import FastAPI, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from app.routers import cases, users
from app.middleware.authentication import AuthMiddleware
from app.config.db_init import db_handler
from app.config import logging_config
from contextlib import asynccontextmanager
import logging
import uvicorn

# Configure logging
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler to manage application startup and shutdown.
    """
    db_handler.connect()  # Connect to MongoDB on startup
    yield
    db_handler.disconnect()  # Disconnect from MongoDB on shutdown
    logger.info("Application shutdown: Disconnected from MongoDB")

def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application.
    """
    app = FastAPI(
        title="Skin Diagnosis System API",
        description="API for diagnosing skin conditions using AI.",
        version="1.0.0",
        lifespan=lifespan  # Register lifespan handler
    )

    # Define a security scheme using HTTP Bearer
    bearer_scheme = HTTPBearer()

    # Add authentication middleware
    app.add_middleware(AuthMiddleware)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(cases.router, prefix="/cases", tags=["Cases"])

    @app.get("/protected-route")
    def protected_route(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
        return {"token": credentials.credentials}

    @app.get("/", tags=["Health"])
    def health_check() -> dict:
        """
        Health check endpoint to verify API is running.
        """
        logger.info("Health check requested")
        return {"message": "Skin Diagnosis API is running"}

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
